# --- demografía.py ---
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


    # 3. DINÁMICA DE TRABAJADORES (Simplificada)
    pob_objetivo = getattr(config, 'num_trabajadores', 1000)
    
    # Ancla de población: estimula la entrada si la población cae por debajo de la meta, y la frena si se supera.
    ancla_poblacion = max(0.1, 2.0 - (poblacion_actual / pob_objetivo)) if pob_objetivo > 0 else 1.0
    
    # Entrada (Nacimiento/Inmigración): Depende positivamente de la tasa de empleo
    tasa_entrada_trabajador = (config.tasa_natalidad + config.prob_inmigracion) * (0.5 + 0.5 * tasa_empleo) * ancla_poblacion
    
    # Cálculo O(1) de nuevos habitantes
    media_entradas = poblacion_actual * tasa_entrada_trabajador if poblacion_actual > 0 else 5.0
    nuevos_habitantes = int(media_entradas) + (1 if rand.random() < (media_entradas % 1) else 0)
    
    for _ in range(nuevos_habitantes):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        # Se le asigna un capital semilla desde el fondo común
        semilla_inicial = estado.presupuesto_referencia_persona * 0.2
        if estado.pool_demografico >= semilla_inicial:
            estado.pool_demografico -= semilla_inicial
            nuevo_trabajador.presupuesto = semilla_inicial
        else:
            nuevo_trabajador.presupuesto = 0.0
        estado.trabajadores.append(nuevo_trabajador)

    # Salidas (Fallecimientos y Emigración)
    sobrevivientes = []
    for t in estado.trabajadores:
        # Inanición: Incrementa progresivamente la mortalidad después de 10 días sin poder comprar
        prob_inanicion = max(0.0, (t.días_sin_comprar - 10) * 0.02)
        prob_muerte = config.tasa_mortalidad + prob_inanicion
        
        # Emigración: Aumenta cuando el empleo en la economía es escaso
        prob_emigracion = config.tasa_emigracion * (2.0 - tasa_empleo)
        
        if rand.random() < (prob_muerte + prob_emigracion):
            # Devolver capital acumulado del trabajador al pozo común
            estado.pool_demografico += t.presupuesto
        else:
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes


    # 4. DINÁMICA DE EMPRESAS (Simplificada)
    emp_objetivo = getattr(config, 'num_empresas', 100)
    
    # Ancla de firmas para mantener el ecosistema balanceado
    ancla_empresas = max(0.1, 2.0 - (num_empresas_actual / emp_objetivo)) if emp_objetivo > 0 else 1.0
    
    # Entrada de Empresas: Depende de la rentabilidad comercial actual
    rentabilidad = presupuesto_promedio_empresa / estado.presupuesto_referencia if estado.presupuesto_referencia > 0 else 1.0
    tasa_entrada_emp = (config.tasa_creacion_empresas + config.tasa_entrada_extranjeras) * max(0.2, min(rentabilidad, 2.0)) * ancla_empresas
    
    # Cálculo O(1) de nuevas empresas
    media_nuevas_emp = num_empresas_actual * tasa_entrada_emp if num_empresas_actual > 0 else 2.0
    nuevas_empresas = int(media_nuevas_emp) + (1 if rand.random() < (media_nuevas_emp % 1) else 0)
    
    for _ in range(nuevas_empresas):
        nueva_emp = Empresa.crear_inicial(config, rand)
        
        # Se dota de capital inicial a la empresa desde el fondo común
        presupuesto_requerido = estado.presupuesto_referencia
        if estado.pool_demografico >= presupuesto_requerido:
            estado.pool_demografico -= presupuesto_requerido
            nueva_emp.presupuesto = presupuesto_requerido
        else:
            seed = max(estado.pool_demografico, presupuesto_requerido * 0.5)
            estado.pool_demografico = max(0.0, estado.pool_demografico - seed)
            nueva_emp.presupuesto = seed
            
        # Heredar condiciones de mercado vigentes (+/- 15% de variabilidad aleatoria)
        if num_empresas_actual > 0:
            nueva_emp.precio = precio_promedio * rand.uniform(0.85, 1.15)
            nueva_emp.salario = max(salario_promedio * rand.uniform(0.85, 1.15), config.salario_mínimo, 1.0)
            nueva_emp.salario_informal = max(salario_informal_promedio * rand.uniform(0.85, 1.15), 1.0)
            nueva_emp.calidad = max(0.0, min(calidad_promedio * rand.uniform(0.9, 1.1), 1.0))
            nueva_emp.satisfacción = max(0.0, min(satisfacción_promedio * rand.uniform(0.9, 1.1), 1.0))
            
        estado.empresas.append(nueva_emp)
        
    # Salidas de Empresas (Quiebras, Cierre por inactividad y Relocalización)
    empresas_activas = []
    for emp in estado.empresas:
        quiebra_financiera = (emp.presupuesto <= 0 and emp.inventario == 0)
        sin_ventas = (emp.días_sin_vender > 90) # Cerrar si lleva 3 meses sin vender
        relocalizacion = (rand.random() < config.tasa_relocalizacion_empresas)
        
        if quiebra_financiera or sin_ventas or relocalizacion:
            # Liquidar el remanente de presupuesto al fondo común
            estado.pool_demografico += max(0.0, emp.presupuesto)
        else:
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas