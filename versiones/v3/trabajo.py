# --- trabajo.py ---
import math

def mercado_laboral(estado):
    random_func = estado.aleatorio.random
    
    # Parámetros estructurales de la Función de Emparejamiento (DMP)
    A_match = 0.8       # Eficiencia de emparejamiento
    gamma_match = 0.5   # Elasticidad del emparejamiento respecto a los desempleados
    
    salario_minimo = estado.config.salario_mínimo
    
    vacantes_formales_pool = []
    vacantes_informales_pool = []
    
    # ==========================================================
    # 1. Decisiones Endógenas de Informalidad por Empresa
    # ==========================================================
    for emp in estado.empresas:
        # Inicializar métricas del periodo laboral
        emp.empleados_formales = 0
        emp.empleados_informales = 0
        emp.productividad_acumulada_formales = 0.0
        emp.productividad_acumulada_informales = 0.0
        
        # Costo de referencia para planificar la contratación
        C_F = max(emp.salario, salario_minimo, 1.0)
        C_I = max(emp.salario_informal, 1.0)
        
        # Umbral de productividad formal basado en el salario mínimo real
        threshold = 0.5 * (salario_minimo / max(emp.precio, 1.0))
        diff = emp.productividad_objetivo - threshold
        
        # Distribución del presupuesto formal vs informal (Margen intensivo)
        phi = 1.0 / (1.0 + math.exp(-5.0 * diff))
        phi = max(0.05, min(phi, 0.95)) # Límites de diversificación
        
        presupuesto_formal = phi * emp.presupuesto
        presupuesto_informal = (1.0 - phi) * emp.presupuesto
        
        # Publicación de vacantes reales en función de presupuestos y costos esperados
        emp.vacantes_formales = min(max(0, int(presupuesto_formal / C_F)), len(estado.trabajadores))
        emp.vacantes_informales = min(max(0, int(presupuesto_informal / C_I)), len(estado.trabajadores))
        
        vacantes_formales_pool.extend([emp] * emp.vacantes_formales)
        vacantes_informales_pool.extend([emp] * emp.vacantes_informales)

    total_trabajadores = len(estado.trabajadores)
    
    # ==========================================================
    # 2. Mercado Formal: Búsqueda y Negociación de Nash
    # ==========================================================
    V_F = len(vacantes_formales_pool)
    U_F = total_trabajadores
    
    matched_worker_indices = set()
    salario_formal_máximo = salario_minimo
    
    if V_F > 0 and U_F > 0:
        # Cantidad agregada de emparejamientos formales bajo fricciones
        M_F = int(min(U_F, V_F, A_match * (U_F ** gamma_match) * (V_F ** (1.0 - gamma_match))))
        
        # Mezclado aleatorio rápido de trabajadores y vacantes para representar emparejamiento estocástico
        workers_indices = list(range(total_trabajadores))
        for i in range(len(workers_indices) - 1, 0, -1):
            j = int(random_func() * (i + 1))
            workers_indices[i], workers_indices[j] = workers_indices[j], workers_indices[i]
            
        for i in range(len(vacantes_formales_pool) - 1, 0, -1):
            j = int(random_func() * (i + 1))
            vacantes_formales_pool[i], vacantes_formales_pool[j] = vacantes_formales_pool[j], vacantes_formales_pool[i]
            
        # Fase de Negociación formal individual
        for idx in range(M_F):
            worker_idx = workers_indices[idx]
            trabajador = estado.trabajadores[worker_idx]
            emp = vacantes_formales_pool[idx]
            
            # Compatibilidad y productividad real obtenida del emparejamiento
            error = abs(trabajador.productividad - emp.productividad_objetivo)
            compatibilidad = max(0.0, 1.0 - error * (1.0 - emp.tolerancia))
            prod_real = trabajador.productividad * compatibilidad
            
            # Valor de reserva del trabajador expresado en salario equivalente
            peso_salario = max(trabajador.sensibilidad_salario * estado.config.sensibilidad_salario, 0.01)
            w_res = trabajador.utilidad_reserva / peso_salario
            
            # Ingreso del producto marginal del trabajo (MRPL)
            mrpl = emp.precio * prod_real
            
            # Negociación de salarios de Nash
            beta_nash = estado.config.poder_trabajadores
            w_nash = beta_nash * mrpl + (1.0 - beta_nash) * w_res
            
            # El salario nominal final está restringido por el salario mínimo legal
            w_formal = max(w_nash, salario_minimo)
            
            # Si el salario mínimo excede la productividad marginal, el contrato no es viable
            if mrpl - w_formal >= 0.0:
                emp.empleados_formales += 1
                emp.productividad_acumulada_formales += trabajador.productividad
                
                trabajador.presupuesto += w_formal
                emp.presupuesto -= w_formal
                
                # Guardar el último salario negociado como referencia de la firma
                emp.salario = w_formal
                salario_formal_máximo = max(salario_formal_máximo, w_formal)
                matched_worker_indices.add(worker_idx)

    # ==========================================================
    # 3. Mercado Informal: Búsqueda y Negociación de Nash
    # ==========================================================
    # Los trabajadores no contratados formalmente buscan en el sector informal
    unmatched_worker_indices = [i for i in range(total_trabajadores) if i not in matched_worker_indices]
    
    V_I = len(vacantes_informales_pool)
    U_I = len(unmatched_worker_indices)
    
    if V_I > 0 and U_I > 0:
        # Cantidad de emparejamientos informales bajo fricciones
        M_I = int(min(U_I, V_I, A_match * (U_I ** gamma_match) * (V_I ** (1.0 - gamma_match))))
        
        # Mezclado aleatorio de los desempleados y de las vacantes informales
        for i in range(len(unmatched_worker_indices) - 1, 0, -1):
            j = int(random_func() * (i + 1))
            unmatched_worker_indices[i], unmatched_worker_indices[j] = unmatched_worker_indices[j], unmatched_worker_indices[i]
            
        for i in range(len(vacantes_informales_pool) - 1, 0, -1):
            j = int(random_func() * (i + 1))
            vacantes_informales_pool[i], vacantes_informales_pool[j] = vacantes_informales_pool[j], vacantes_informales_pool[i]
            
        # Fase de Negociación informal individual
        for idx in range(M_I):
            worker_idx = unmatched_worker_indices[idx]
            trabajador = estado.trabajadores[worker_idx]
            emp = vacantes_informales_pool[idx]
            
            # Penalización de productividad en la informalidad (por falta de capital regulado)
            informal_discount = 0.8
            error = abs(trabajador.productividad - emp.productividad_objetivo)
            compatibilidad = max(0.0, 1.0 - error * (1.0 - emp.tolerancia))
            prod_real = trabajador.productividad * compatibilidad * informal_discount
            
            # Salario de reserva
            peso_salario = max(trabajador.sensibilidad_salario * estado.config.sensibilidad_salario, 0.01)
            w_res = trabajador.utilidad_reserva / peso_salario
            
            # Productividad marginal en el sector informal
            mrpl = emp.precio * prod_real
            
            # Costo esperado de multas/auditoría para la empresa informal (cuña de riesgo)
            tau_I = 0.05 * mrpl
            
            # Negociación de Nash sobre el excedente informal libre de riesgo
            beta_nash = estado.config.poder_trabajadores
            w_nash = beta_nash * (mrpl - tau_I) + (1.0 - beta_nash) * w_res
            w_informal = max(w_nash, 1.0)
            
            # Verificación de viabilidad del contrato informal para la empresa
            if mrpl - w_informal - tau_I >= 0.0:
                emp.empleados_informales += 1
                emp.productividad_acumulada_informales += trabajador.productividad * informal_discount
                
                trabajador.presupuesto += w_informal
                emp.presupuesto -= w_informal
                
                emp.salario_informal = w_informal

    # ==========================================================
    # 4. Actualización Regulatoria (Salario Mínimo Automático)
    # ==========================================================
    num_empleados_formales = sum(empresa.empleados_formales for empresa in estado.empresas)
    
    if estado.config.salario_mínimo_automático and estado.día % estado.config.salario_mínimo_automático_intervalo == 0:
        if total_trabajadores > 0:
            tasa_empleo = num_empleados_formales / total_trabajadores
        else:
            tasa_empleo = 0.0
            
        tasa_límite = estado.config.salario_mínimo_automático_formalidad_límite
        reducción = estado.config.salario_mínimo_automático_reducción
        aumento = estado.config.salario_mínimo_automático_aumento

        if estado.config.salario_mínimo == 0:
            estado.config.salario_mínimo = salario_formal_máximo * estado.config.tasa_salario_mínimo * (aumento - 1)
        if tasa_empleo > tasa_límite * 1.05:
            estado.config.salario_mínimo = min(estado.config.salario_mínimo * aumento, salario_formal_máximo * estado.config.tasa_salario_mínimo)
        elif tasa_empleo < tasa_límite * 0.95:
            estado.config.salario_mínimo *= reducción

    # Guardar métricas de pago reales de las empresas para reporte estadístico
    for empresa in estado.empresas:
        empresa.salario_pago_real = empresa.salario
        empresa.salario_informal_pago_real = empresa.salario_informal

        # Ajuste de límites mínimos para futuras planificaciones
        empresa.salario = max(empresa.salario, estado.config.salario_mínimo, 1.0)
        empresa.salario_informal = max(empresa.salario_informal, 1.0)