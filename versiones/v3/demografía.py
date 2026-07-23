# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    
    # 1. CÁLCULO DE PROMEDIOS EN TIEMPO REAL
    poblacion_actual = len(estado.trabajadores)
    num_empresas_actual = len(estado.empresas)
    
    # Fondo demográfico para garantizar la conservación del dinero en el sistema
    if not hasattr(estado, 'pool_demografico'):
        estado.pool_demografico = 0.0

    # Promedios de mercado actuales
    if num_empresas_actual > 0:
        presupuesto_promedio_empresa = sum(e.presupuesto for e in estado.empresas) / num_empresas_actual
        precio_promedio = sum(e.precio for e in estado.empresas) / num_empresas_actual
        salario_promedio = sum(e.salario for e in estado.empresas) / num_empresas_actual
        salario_informal_promedio = sum(e.salario_informal for e in estado.empresas) / num_empresas_actual
        calidad_promedio = sum(e.calidad for e in estado.empresas) / num_empresas_actual
        satisfacción_promedio = sum(e.satisfacción for e in estado.empresas) / num_empresas_actual
        
        # Suavizado EMA de 365 días para adaptar referencias de largo plazo
        alpha = 1 / 365
        estado.salario_referencia += (salario_promedio - estado.salario_referencia) * alpha
        estado.salario_informal_referencia += (salario_informal_promedio - estado.salario_informal_referencia) * alpha
        estado.precio_referencia += (precio_promedio - estado.precio_referencia) * alpha
        estado.presupuesto_referencia += (presupuesto_promedio_empresa - estado.presupuesto_referencia) * alpha
    else:
        precio_promedio = estado.precio_referencia
        salario_promedio = estado.salario_referencia
        salario_informal_promedio = estado.salario_informal_referencia
        presupuesto_promedio_empresa = estado.presupuesto_referencia

    if poblacion_actual > 0:
        presupuesto_promedio_trabajador = sum(t.presupuesto for t in estado.trabajadores) / poblacion_actual
        alpha = 1 / 365
        estado.presupuesto_referencia_persona += (presupuesto_promedio_trabajador - estado.presupuesto_referencia_persona) * alpha
    else:
        presupuesto_promedio_trabajador = 0.0

    # 2. DEFINICIÓN DE FACTORES DE ESCALA Y ANCLA DEMOGRÁFICA
    poblacion_referencia = getattr(config, 'num_trabajadores', 1000.0)
    factor_escala = max(1.0, poblacion_actual / poblacion_referencia)
    
    # Amortiguador suave para evitar sobrepoblación o colapso
    ancla_demografica = max(0.2, 1.5 - 0.5 * (poblacion_actual / poblacion_referencia))

    # 3. DINÁMICA DE PERSONAS
    num_formales = sum(e.empleados_formales for e in estado.empresas)
    num_informales = sum(e.empleados_informales for e in estado.empresas)
    
    # Tasa de empleo como termómetro principal de la salud económica
    tasa_empleo = (num_formales + num_informales) / poblacion_actual if poblacion_actual > 0 else 0.0
    factor_economico = max(0.1, tasa_empleo) 

    # Tasas dinámicas basadas en la economía y el ancla demográfica
    tasa_natalidad_dinamica = config.tasa_natalidad * factor_economico * ancla_demografica
    prob_inmigracion_dinamica = config.prob_inmigracion * factor_economico * ancla_demografica

    # Cálculo O(1) de entradas utilizando la esperanza matemática
    media_nacimientos = poblacion_actual * tasa_natalidad_dinamica
    nuevos_nacidos = int(media_nacimientos) + (1 if rand.random() < (media_nacimientos % 1) else 0)
    
    media_inmigrantes = prob_inmigracion_dinamica * factor_escala
    nuevos_inmigrantes = int(media_inmigrantes) + (1 if rand.random() < (media_inmigrantes % 1) else 0)
    
    nuevos_habitantes = nuevos_nacidos + nuevos_inmigrantes
    
    for _ in range(nuevos_habitantes):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        # Se extrae un pequeño capital inicial del fondo común si hay fondos disponibles
        semilla_inicial = estado.presupuesto_referencia_persona * 0.1
        if estado.pool_demografico >= semilla_inicial:
            estado.pool_demografico -= semilla_inicial
            nuevo_trabajador.presupuesto = semilla_inicial
        else:
            nuevo_trabajador.presupuesto = 0.0
        estado.trabajadores.append(nuevo_trabajador)

    # Salidas (Mortalidad e Emigración)
    tasa_emigracion_dinamica = min(0.95, config.tasa_emigracion * (1.0 + 5.0 * (1.0 - tasa_empleo)))
    
    sobrevivientes = []
    for t in estado.trabajadores:
        # Inanición lineal simple (se incrementa 2% diario a partir del día 10 sin comprar)
        prob_inanicion = max(0.0, (t.días_sin_comprar - 10) * 0.02)
        
        fallece = rand.random() < (config.tasa_mortalidad + prob_inanicion)
        emigra = rand.random() < tasa_emigracion_dinamica
        
        if fallece or emigra:
            # El presupuesto acumulado del agente se devuelve al fondo del sistema
            estado.pool_demografico += t.presupuesto
        else:
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes

    # 4. DINÁMICA DE EMPRESAS
    rentabilidad = presupuesto_promedio_empresa / estado.presupuesto_referencia if estado.presupuesto_referencia > 0 else 1.0
    
    # Se unifican la creación y entrada extranjera en un indicador de entrada simplificado
    tasa_entrada_total = config.tasa_creacion_empresas + config.tasa_entrada_extranjeras
    prob_entrada = tasa_entrada_total * max(0.2, min(rentabilidad, 2.0))
    
    # Cálculo O(1) de nuevas empresas
    media_nuevas = prob_entrada * (factor_escala ** 0.6)
    nuevas_empresas = int(media_nuevas) + (1 if rand.random() < (media_nuevas % 1) else 0)
    
    for _ in range(nuevas_empresas):
        nueva_emp = Empresa.crear_inicial(config, rand)
        
        # El capital inicial proviene del pool acumulado (o fallback parcial si está seco)
        presupuesto_requerido = estado.presupuesto_referencia
        if estado.pool_demografico >= presupuesto_requerido:
            estado.pool_demografico -= presupuesto_requerido
            nueva_emp.presupuesto = presupuesto_requerido
        else:
            seed = max(estado.pool_demografico, presupuesto_requerido * 0.5)
            estado.pool_demografico = max(0.0, estado.pool_demografico - seed)
            nueva_emp.presupuesto = seed
            
        # Heredar condiciones promedio del mercado actual con margen de variación (+/- 15%)
        if num_empresas_actual > 0:
            nueva_emp.precio = precio_promedio * rand.uniform(0.85, 1.15)
            nueva_emp.salario = max(salario_promedio * rand.uniform(0.85, 1.15), config.salario_mínimo, 1.0)
            nueva_emp.salario_informal = max(salario_informal_promedio * rand.uniform(0.85, 1.15), 1.0)
            nueva_emp.calidad = max(0.0, min(calidad_promedio * rand.uniform(0.9, 1.1), 1.0))
            nueva_emp.satisfacción = max(0.0, min(satisfacción_promedio * rand.uniform(0.9, 1.1), 1.0))
            
        estado.empresas.append(nueva_emp)
        
    # Salidas (Quiebras y Cierres)
    empresas_activas = []
    # Umbral de viabilidad financiera simple (10% de la referencia histórica)
    benchmark_cierre = 0.1 * estado.presupuesto_referencia
    
    for emp in estado.empresas:
        quiebra_financiera = (emp.presupuesto <= 0 and emp.inventario == 0) or (emp.días_sin_vender > 120)
        cierre_exogeno = (emp.presupuesto < benchmark_cierre) and (rand.random() < 0.05)
        relocalizacion = rand.random() < config.tasa_relocalizacion_empresas
        
        if quiebra_financiera or cierre_exogeno or relocalizacion:
            # Liquidación del capital restante de la empresa al fondo demográfico
            estado.pool_demografico += max(0.0, emp.presupuesto)
        else:
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas