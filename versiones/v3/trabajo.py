# --- trabajo.py ---

def mercado_laboral(estado):
    # Lista unificada de vacantes. Guardaremos tuplas: (empresa, es_formal)
    vacantes_disponibles = []

    # 1. Generación de vacantes proyectadas iniciales
    for empresa in estado.empresas:
        salario_seguro = max(empresa.salario, 1.0)
        empresa.vacantes_formales = min(
            int(empresa.presupuesto / salario_seguro),
            estado.config.num_trabajadores
        )
        # Añadimos las vacantes formales a la bolsa unificada
        vacantes_disponibles.extend([(empresa, True)] * empresa.vacantes_formales)

        salario_inf_seguro = max(empresa.salario_informal, 1.0)
        empresa.vacantes_informales = min(
            int(empresa.presupuesto / salario_inf_seguro),
            estado.config.num_trabajadores
        )
        # Añadimos las vacantes informales a la bolsa unificada
        vacantes_disponibles.extend([(empresa, False)] * empresa.vacantes_informales)

        # Inicializamos los contadores de contratación para el día de hoy
        empresa.empleados_formales = 0
        empresa.empleados_informales = 0

    # Escalas globales de sensibilidad (puedes definirlas en tu config o usar fallbacks)
    sc_salario = getattr(estado.config, 'sensibilidad_salario', 1.0)
    sc_seguridad = getattr(estado.config, 'sensibilidad_seguridad', 1.0)
    sc_estabilidad = getattr(estado.config, 'sensibilidad_estabilidad', 1.0)

    rand = estado.aleatorio
    random_func = rand.random

    salario_formal_máximo = estado.config.salario_mínimo

    # 2. Emparejamiento de trabajadores y vacantes
    for trabajador in estado.trabajadores:
        n_disp = len(vacantes_disponibles)
        if n_disp > 0:
            # Sensibilidades individuales con fallbacks en caso de que no existan atributos todavía
            peso_salario = getattr(trabajador, 'sensibilidad_salario', 1.0) * sc_salario
            peso_seguridad = getattr(trabajador, 'sensibilidad_seguridad', 1.0) * sc_seguridad
            peso_estabilidad = getattr(trabajador, 'sensibilidad_estabilidad', 1.0) * sc_estabilidad

            k = min(10, n_disp)
            
            # Muestreo ultra rápido de k índices únicos (Rejection Sampling)
            indices = []
            if k == n_disp:
                indices = list(range(n_disp))
            else:
                seen = set()
                for _ in range(k):
                    idx = int(random_func() * n_disp)
                    while idx in seen:
                        idx = int(random_func() * n_disp)
                    seen.add(idx)
                    indices.append(idx)
            
            # Búsqueda de la mejor vacante viable según el Score
            best_idx_in_list = -1
            best_score = -float('inf')
            seleccionada = None
            es_formal_seleccionada = True
            
            for idx in indices:
                emp, es_formal = vacantes_disponibles[idx]
                salario_propuesto = emp.salario if es_formal else emp.salario_informal
                
                # Control dinámico del presupuesto: la empresa debe poder costearlo en este momento
                if emp.presupuesto >= salario_propuesto:
                    # Atributos evaluados de la vacante
                    valor_seguridad = 100.0 if es_formal else 0.0          # Premio por formalidad
                    valor_estabilidad = emp.productividad                 # Atractivo estructural de la empresa
                    
                    score = (salario_propuesto * peso_salario) + \
                            (valor_seguridad * peso_seguridad) + \
                            (valor_estabilidad * peso_estabilidad)
                    
                    if score > best_score:
                        best_score = score
                        best_idx_in_list = idx
                        seleccionada = emp
                        es_formal_seleccionada = es_formal

            # 3. Transacción y contratación si se encontró una opción viable
            if seleccionada is not None:
                salario_pago = seleccionada.salario if es_formal_seleccionada else seleccionada.salario_informal
                
                if es_formal_seleccionada:
                    seleccionada.empleados_formales += 1
                    salario_formal_máximo = max(salario_formal_máximo, seleccionada.salario)
                else:
                    seleccionada.empleados_informales += 1

                # Modificación de presupuestos
                trabajador.presupuesto += salario_pago
                seleccionada.presupuesto -= salario_pago
                
                # Eliminación O(1) con swap-and-pop de la vacante tomada
                last_idx = len(vacantes_disponibles) - 1
                if best_idx_in_list != last_idx:
                    vacantes_disponibles[best_idx_in_list] = vacantes_disponibles[last_idx]
                vacantes_disponibles.pop()
        else:
            # No quedan vacantes disponibles en el mercado
            break

    # =========================================================================
    # Ajustes salariales de fin de jornada (se mantiene la lógica original)
    # =========================================================================
    
    # Calcular proyecciones
    vacantes_formales_proyectadas = estado.config.num_trabajadores / estado.config.num_empresas
    num_empleados_formales = sum([empresa.empleados_formales for empresa in estado.empresas])
    num_empleados_informales_proyectados = estado.config.num_trabajadores - num_empleados_formales
    vacantes_informales_proyectadas = (num_empleados_informales_proyectados * estado.config.informalidad_por_empresa) / estado.config.num_empresas

    # Actualizar salario mínimo si aplica
    if estado.config.salario_mínimo_automático and estado.día % estado.config.salario_mínimo_automático_intervalo == 0:
        tasa_empleo = num_empleados_formales / estado.config.num_trabajadores
        tasa_límite = estado.config.salario_mínimo_automático_formalidad_límite
        reducción = estado.config.salario_mínimo_automático_reducción
        aumento = estado.config.salario_mínimo_automático_aumento
        if tasa_empleo > tasa_límite * 1.05:
            if estado.config.salario_mínimo > 1:
                estado.config.salario_mínimo = min(estado.config.salario_mínimo * aumento, salario_formal_máximo * estado.config.tasa_salario_mínimo)
            else:
                estado.config.salario_mínimo = salario_formal_máximo * estado.config.tasa_salario_mínimo * reducción
        elif tasa_empleo < tasa_límite * 0.95:
            estado.config.salario_mínimo *= reducción

    # Ajustes individuales de salarios de las empresas basados en vacantes restantes
    for empresa in estado.empresas:
        empresa.salario_pago_real = empresa.salario
        empresa.salario_informal_pago_real = empresa.salario_informal

        ratio = (empresa.vacantes_formales - vacantes_formales_proyectadas) * 0.3
        empresa.salario *= 1 + ratio / 100
        empresa.salario = max(empresa.salario, estado.config.salario_mínimo, 1.0)

        ratio = (empresa.vacantes_informales - vacantes_informales_proyectadas) * 0.3
        empresa.salario_informal *= 1 + ratio / 100
        empresa.salario_informal = max(empresa.salario_informal, 1.0)