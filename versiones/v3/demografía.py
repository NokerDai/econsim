# --- demografía.py ---
import math
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    
    # 1. INICIALIZACIÓN DE REFERENCIAS Y FONDO DEMOGRÁFICO (Si no existen)
    if not hasattr(estado, 'pool_demografico'):
        estado.pool_demografico = 0.0
    if not hasattr(estado, 'salario_referencia'):
        estado.salario_referencia = getattr(config, 'salario_inicial', 10.0)
    if not hasattr(estado, 'salario_informal_referencia'):
        estado.salario_informal_referencia = getattr(config, 'salario_informal_inicial', 8.0)
    if not hasattr(estado, 'precio_referencia'):
        estado.precio_referencia = getattr(config, 'precio_inicial', 5.0)
    if not hasattr(estado, 'presupuesto_referencia'):
        estado.presupuesto_referencia = getattr(config, 'presupuesto_inicial', 100.0)
    if not hasattr(estado, 'presupuesto_referencia_persona'):
        estado.presupuesto_referencia_persona = getattr(config, 'presupuesto_inicial', 100.0) * 0.1

    # Poblaciones actuales
    poblacion_actual = len(estado.trabajadores)
    num_empresas_actual = len(estado.empresas)

    # 2. CÁLCULO DE PROMEDIOS DE MERCADO ACTUALES
    if num_empresas_actual > 0:
        precio_promedio = sum(e.precio for e in estado.empresas) / num_empresas_actual
        salario_promedio = sum(e.salario for e in estado.empresas) / num_empresas_actual
        salario_informal_promedio = sum(e.salario_informal for e in estado.empresas) / num_empresas_actual
        presupuesto_promedio_empresa = sum(e.presupuesto for e in estado.empresas) / num_empresas_actual
        calidad_promedio = sum(e.calidad for e in estado.empresas) / num_empresas_actual
        satisfacción_promedio = sum(e.satisfacción for e in estado.empresas) / num_empresas_actual
        
        # Suavizado simple (adaptación del 5% diario para referencias estables)
        estado.salario_referencia = 0.95 * estado.salario_referencia + 0.05 * salario_promedio
        estado.salario_informal_referencia = 0.95 * estado.salario_informal_referencia + 0.05 * salario_informal_promedio
        estado.precio_referencia = 0.95 * estado.precio_referencia + 0.05 * precio_promedio
        estado.presupuesto_referencia = 0.95 * estado.presupuesto_referencia + 0.05 * presupuesto_promedio_empresa
    else:
        precio_promedio = estado.precio_referencia
        salario_promedio = estado.salario_referencia
        salario_informal_promedio = estado.salario_informal_referencia
        presupuesto_promedio_empresa = estado.presupuesto_referencia
        calidad_promedio = 0.5
        satisfacción_promedio = 0.5

    if poblacion_actual > 0:
        presupuesto_promedio_trabajador = sum(t.presupuesto for t in estado.trabajadores) / poblacion_actual
        estado.presupuesto_referencia_persona = 0.95 * estado.presupuesto_referencia_persona + 0.05 * presupuesto_promedio_trabajador
    else:
        presupuesto_promedio_trabajador = 0.0

    # Tasa de empleo (salud de la economía)
    num_formales = sum(e.empleados_formales for e in estado.empresas)
    num_informales = sum(e.empleados_informales for e in estado.empresas)
    tasa_empleo = (num_formales + num_informales) / poblacion_actual if poblacion_actual > 0 else 0.0


    # 3. DINÁMICA DE TRABAJADORES (Enfoque micro moderno)
    pob_objetivo = getattr(config, 'num_trabajadores', 1000)
    
    # Ancla de población para calibración macro
    ancla_poblacion = max(0.1, 2.0 - (poblacion_actual / pob_objetivo)) if pob_objetivo > 0 else 1.0
    
    # Envejecimiento biológico de los trabajadores (se asume incremento diario)
    for t in estado.trabajadores:
        if not hasattr(t, 'edad'):
            t.edad = rand.uniform(18, 65)
        else:
            t.edad += 1.0 / 365.0

    # A) Nacimientos (Modelo de Elección Familiar de Becker)
    # Se introduce el costo de crianza 'q_crianza' proporcional al presupuesto promedio.
    # Los agentes en edad fértil (18 a 45 años) evalúan la fertilidad en función de su ingreso/riqueza.
    q_crianza = max(estado.presupuesto_referencia_persona * 0.3, 1.0)
    nuevos_nacimientos = 0
    
    if poblacion_actual > 0:
        for t in estado.trabajadores:
            if 18 <= t.edad <= 45:
                # Decisión de consumo vs hijos: la probabilidad aumenta a mayor presupuesto relativo
                prob_fertilidad = config.tasa_natalidad * min(2.0, t.presupuesto / q_crianza) * ancla_poblacion
                if rand.random() < prob_fertilidad:
                    nuevos_nacimientos += 1
                    t.presupuesto = max(0.0, t.presupuesto - q_crianza)  # Costo de crianza deducido
    else:
        # Tasa de rescate demográfico si no hay sobrevivientes
        nuevos_nacimientos = int(5.0 * ancla_poblacion)

    # B) Migración Entrante (Logit de elección discreta)
    # El valor del destino local V_d depende de la tasa de empleo y del nivel de precios.
    # Se compara con un valor externo de reserva (V_externo) descontando el costo de migración.
    V_d_local = tasa_empleo - 0.1 * (precio_promedio / max(1e-9, estado.precio_referencia))
    V_externo = -0.5
    costo_migracion_in = 0.5
    
    diff_in = V_d_local - V_externo - costo_migracion_in
    diff_in = min(10.0, max(-10.0, diff_in))  # Evitar desbordamiento en exp
    prob_inmigracion_logit = 1.0 / (1.0 + math.exp(-diff_in))
    
    media_inmigrantes = (poblacion_actual if poblacion_actual > 0 else 10.0) * config.prob_inmigracion * prob_inmigracion_logit * ancla_poblacion
    nuevos_inmigrantes = int(media_inmigrantes) + (1 if rand.random() < (media_inmigrantes % 1) else 0)

    # Añadir nuevos agentes al sistema
    total_nuevos = nuevos_nacimientos + nuevos_inmigrantes
    for _ in range(total_nuevos):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        nuevo_trabajador.edad = rand.uniform(18, 25)  # Nuevos integrantes comienzan jóvenes
        
        # Asignación de capital inicial básico desde el pozo común
        semilla_inicial = estado.presupuesto_referencia_persona * 0.2
        if estado.pool_demografico >= semilla_inicial:
            estado.pool_demografico -= semilla_inicial
            nuevo_trabajador.presupuesto = semilla_inicial
        else:
            nuevo_trabajador.presupuesto = 0.0
        estado.trabajadores.append(nuevo_trabajador)

    # C) Decisión de Muerte (Logística) y Emigración (Logit)
    sobrevivientes = []
    for t in estado.trabajadores:
        # Probabilidad de Muerte Logística: dependiente de edad, salud y riqueza
        salud = max(0.0, 1.0 - t.días_sin_comprar * 0.05)
        riqueza_relativa = t.presupuesto / max(1e-9, estado.presupuesto_referencia_persona)
        
        # Parámetros calibrados: edad aumenta mortalidad, salud e ingresos la reducen
        z_muerte = -9.0 + 0.08 * t.edad - 3.0 * salud - 1.0 * riqueza_relativa
        z_muerte = min(10.0, max(-10.0, z_muerte))
        prob_muerte = 1.0 / (1.0 + math.exp(-z_muerte))
        prob_muerte *= config.tasa_mortalidad * 100.0  # Escalamiento según el config general

        # Probabilidad de Emigración (Modelo de Elección Logit):
        # El agente compara la utilidad en el origen (V_o) con el destino externo (V_d_ext)
        V_o_local = -0.5 * t.días_sin_comprar + 0.5 * riqueza_relativa
        V_d_ext = 1.0  # Valor externo de reserva
        costo_migracion_out = 1.5
        
        diff_out = V_o_local - V_d_ext + costo_migracion_out
        diff_out = min(10.0, max(-10.0, diff_out))
        prob_emigracion = 1.0 / (1.0 + math.exp(diff_out))
        prob_emigracion *= config.tasa_emigracion * 10.0

        if rand.random() < prob_muerte or rand.random() < prob_emigracion:
            # Los activos del agente que se retira vuelven al pool demográfico
            estado.pool_demografico += t.presupuesto
        else:
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes


    # 4. DINÁMICA DE EMPRESAS (Enfoque micro moderno)
    emp_objetivo = getattr(config, 'num_empresas', 100)
    
    # Ancla de cantidad de firmas
    ancla_empresas = max(0.1, 2.0 - (num_empresas_actual / emp_objetivo)) if emp_objetivo > 0 else 1.0
    
    # A) Entrada de Empresas (Decisión de Beneficio Esperado y Logit)
    # Se calcula la expectativa de beneficio corriente (precio * ventas - salarios pagados)
    if num_empresas_actual > 0:
        ventas_promedio_emp = sum(e.ventas_hoy for e in estado.empresas) / num_empresas_actual
        empleados_promedio_emp = (num_formales + num_informales) / num_empresas_actual
        E_pi = (precio_promedio * ventas_promedio_emp) - (salario_promedio * empleados_promedio_emp)
    else:
        E_pi = estado.precio_referencia * 2.0 - estado.salario_referencia

    # Costo fijo de entrada F_e
    F_e = estado.presupuesto_referencia
    norm_emp = max(estado.presupuesto_referencia, 1.0)
    diff_entry = (E_pi - F_e) / norm_emp
    diff_entry = min(10.0, max(-10.0, diff_entry))
    
    # Probabilidad de entrada por modelo Logit
    prob_entry = 1.0 / (1.0 + math.exp(-diff_entry))
    tasa_entrada_emp = (config.tasa_creacion_empresas + config.tasa_entrada_extranjeras) * prob_entry * ancla_empresas
    
    media_nuevas_emp = num_empresas_actual * tasa_entrada_emp if num_empresas_actual > 0 else 2.0
    nuevas_empresas = int(media_nuevas_emp) + (1 if rand.random() < (media_nuevas_emp % 1) else 0)
    
    for _ in range(nuevas_empresas):
        nueva_emp = Empresa.crear_inicial(config, rand)
        
        presupuesto_requerido = estado.presupuesto_referencia
        if estado.pool_demografico >= presupuesto_requerido:
            estado.pool_demografico -= presupuesto_requerido
            nueva_emp.presupuesto = presupuesto_requerido
        else:
            seed = max(estado.pool_demografico, presupuesto_requerido * 0.5)
            estado.pool_demografico = max(0.0, estado.pool_demografico - seed)
            nueva_emp.presupuesto = seed
            
        # Heredar condiciones iniciales del ecosistema
        if num_empresas_actual > 0:
            nueva_emp.precio = precio_promedio * rand.uniform(0.85, 1.15)
            nueva_emp.salario = max(salario_promedio * rand.uniform(0.85, 1.15), config.salario_mínimo, 1.0)
            nueva_emp.salario_informal = max(salario_informal_promedio * rand.uniform(0.85, 1.15), 1.0)
            nueva_emp.calidad = max(0.0, min(calidad_promedio * rand.uniform(0.9, 1.1), 1.0))
            nueva_emp.satisfacción = max(0.0, min(satisfacción_promedio * rand.uniform(0.9, 1.1), 1.0))
            
        estado.empresas.append(nueva_emp)
        
    # B) Quiebra / Salida de Empresas (Decisión Intertemporal y Umbral Hopenhayn)
    # Se introduce el factor de descuento beta_disc para evaluar el valor de continuación.
    # Adicionalmente, se define una productividad mínima viable 'phi_star' para firmas poco competitivas.
    beta_disc = 0.95
    phi_star = 0.2
    if num_empresas_actual > 0:
        productividad_promedio_emp = sum(e.productividad for e in estado.empresas) / num_empresas_actual
        phi_star = max(0.1, 0.3 * productividad_promedio_emp)

    empresas_sobrevivientes = []
    for emp in estado.empresas:
        # Beneficio neto del periodo
        costos_laborales = (emp.empleados_formales * emp.salario) + (emp.empleados_informales * emp.salario_informal)
        pi_t = (emp.ventas_hoy * emp.precio) - costos_laborales
        
        # Valor de continuar: capital actual + flujo presente + flujo futuro esperado descontado
        V_continue = emp.presupuesto + pi_t + beta_disc * pi_t
        
        quiebra_financiera = (V_continue < 0) or (emp.presupuesto <= 0 and emp.inventario == 0)
        bajo_productivo = emp.productividad < phi_star  # Selección natural por productividad
        sin_ventas = (emp.días_sin_vender > 90)
        
        if quiebra_financiera or bajo_productivo or sin_ventas:
            # Los fondos remanentes se reintegran al pool común
            estado.pool_demografico += max(0.0, emp.presupuesto)
        else:
            empresas_sobrevivientes.append(emp)

    # C) Relocalización de Empresas (Decisión Espacial Logit)
    # Comparación de beneficios locales (pi_i) versus beneficios esperados en otra región (E_pi) menos costos de relocalización (costo_reloc)
    empresas_activas = []
    for emp in empresas_sobrevivientes:
        costos_laborales = (emp.empleados_formales * emp.salario) + (emp.empleados_informales * emp.salario_informal)
        pi_i = (emp.ventas_hoy * emp.precio) - costos_laborales
        costo_reloc = estado.presupuesto_referencia * 0.2
        
        diff_move = ((E_pi - costo_reloc) - pi_i) / norm_emp
        diff_move = min(10.0, max(-10.0, diff_move))
        
        prob_reloc = 1.0 / (1.0 + math.exp(-diff_move))
        prob_reloc *= config.tasa_relocalizacion_empresas
        
        if rand.random() < prob_reloc:
            # Liquidación del capital al pool común y salida del mercado local
            estado.pool_demografico += max(0.0, emp.presupuesto)
        else:
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas