# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    
    # ==========================================
    # 1. CÁLCULO DE PROMEDIOS EN TIEMPO REAL
    # ==========================================
    
    # Promedios de los trabajadores actuales
    poblacion_actual = len(estado.trabajadores)
    if poblacion_actual > 0:
        presupuesto_promedio_trabajador = sum(t.presupuesto for t in estado.trabajadores) / poblacion_actual
    else:
        presupuesto_promedio_trabajador = 0.0

    # Promedios de las empresas actuales
    num_empresas_actual = len(estado.empresas)
    if num_empresas_actual > 0:
        presupuesto_promedio_empresa = sum(e.presupuesto for e in estado.empresas) / num_empresas_actual
        precio_promedio = sum(e.precio for e in estado.empresas) / num_empresas_actual
        salario_promedio = sum(e.salario for e in estado.empresas) / num_empresas_actual
        salario_informal_promedio = sum(e.salario_informal for e in estado.empresas) / num_empresas_actual
        trigger = True
        calidad_promedio = sum(e.calidad for e in estado.empresas) / num_empresas_actual
        satisfacción_promedio = sum(e.satisfacción for e in estado.empresas) / num_empresas_actual
        productividad_objetivo_promedio = sum(e.productividad_objetivo for e in estado.empresas) / num_empresas_actual
        tolerancia_promedio = sum(e.tolerancia for e in estado.empresas) / num_empresas_actual
    else:
        # Respaldo a los valores de referencia del estado si el mercado se queda sin empresas
        presupuesto_promedio_empresa = estado.presupuesto_referencia
        precio_promedio = estado.precio_referencia
        salario_promedio = estado.salario_referencia
        salario_informal_promedio = estado.salario_informal_referencia
        trigger = False

    # Actualizar referencias lentamente todos los días (promedio móvil exponencial)
    if num_empresas_actual > 0:
        alpha = 1 / 365
        estado.salario_referencia += (salario_promedio - estado.salario_referencia) * alpha
        estado.salario_informal_referencia += (salario_informal_promedio - estado.salario_informal_referencia) * alpha
        estado.precio_referencia += (precio_promedio - estado.precio_referencia) * alpha
        estado.presupuesto_referencia += (presupuesto_promedio_empresa - estado.presupuesto_referencia) * alpha
        estado.presupuesto_referencia_persona += (presupuesto_promedio_trabajador - estado.presupuesto_referencia_persona) * alpha

    # ==========================================
    # DEFINICIÓN DEL FACTOR DE ESCALA
    # ==========================================
    # Intentamos obtener la población inicial de la configuración; si no existe, usamos 100 como base.
    poblacion_referencia = getattr(config, 'num_trabajadores', 100.0)
    
    # El factor de escala nos dice cuántas veces más grande es la población actual respecto a la base.
    # El mínimo de 1.0 asegura que la tasa de entrada nominal no caiga por debajo de la original.
    factor_escala = max(1.0, poblacion_actual / poblacion_referencia)

    # ==========================================
    # 2. DINÁMICA DE PERSONAS
    # ==========================================
    
    # --- Entradas (Natalidad e Inmigración) ---
    nuevos_habitantes = 0
    
    # Nacimientos (depende del poder de compra promedio de los trabajadores con respecto a la referencia)
    poder_de_compra = (presupuesto_promedio_trabajador / precio_promedio) / (estado.presupuesto_referencia_persona / estado.precio_referencia) if precio_promedio > 0 and estado.precio_referencia * estado.presupuesto_referencia_persona > 0 else 1.0
    tasa_natalidad_dinamica = config.tasa_natalidad * min(max(poder_de_compra, 0.5), 2.0)
    
    for _ in range(poblacion_actual):
        if rand.random() < tasa_natalidad_dinamica:
            nuevos_habitantes += 1
            
    # Inmigración escalada proporcionalmente
    prob_inmigracion_dinamica = config.prob_inmigracion * min(max(poder_de_compra, 0.5), 2.0)
    
    # CORRECCIÓN: El número de "intentos" de inmigración diarios escala con la población actual.
    # Se usa max(1, ...) para que si la población se extingue temporalmente (poblacion_actual == 0),
    # todavía exista un intento unitario que permita repoblar el sistema.
    intentos_inmigracion = max(1, int(factor_escala))
    for _ in range(intentos_inmigracion):
        if rand.random() < prob_inmigracion_dinamica:
            nuevos_habitantes += 1
        
    # Inicialización e inserción de nuevos trabajadores en el estado
    for _ in range(nuevos_habitantes):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        nuevo_trabajador.presupuesto = rand.uniform(
            presupuesto_promedio_trabajador * 0.75, 
            presupuesto_promedio_trabajador * 1.25
        )
        estado.trabajadores.append(nuevo_trabajador)
        
    # --- Salidas (Mortalidad y Emigración) ---
    # Calcular desempleo usando el método oficial del collector
    num_formales = sum(e.empleados_formales for e in estado.empresas)
    num_informales = sum(e.empleados_informales for e in estado.empresas)
    if poblacion_actual > 0:
        tasa_formal = num_formales / poblacion_actual
        tasa_informal = num_informales / poblacion_actual
        tasa_desempleo = max(0.0, 1.0 - tasa_formal - tasa_informal)
    else:
        tasa_desempleo = 0.0

    tasa_emigracion_dinamica = config.tasa_emigracion * (1.0 + tasa_desempleo)
    
    sobrevivientes = []
    for t in estado.trabajadores:
        fallece = rand.random() < config.tasa_mortalidad or t.días_sin_comprar > 30
        emigra = rand.random() < tasa_emigracion_dinamica
        
        # Si no fallece ni emigra, permanece en el sistema
        if not (fallece or emigra):
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes

    # ==========================================
    # 3. DINÁMICA DE EMPRESAS
    # ==========================================
    
    # --- Entradas (Creación y Entrada Extranjera) ---
    nuevas_empresas = 0
    
    # Emprendimiento local (depende de la rentabilidad media comparada con la referencia)
    rentabilidad = presupuesto_promedio_empresa / estado.presupuesto_referencia if estado.presupuesto_referencia > 0 else 1.0
    prob_creacion = config.tasa_creacion_empresas * min(max(rentabilidad, 0.2), 3.0)
    
    # CORRECCIÓN: Los intentos de creación de empresas locales escalan con la población (más personas -> más emprendedores potenciales)
    intentos_creacion = max(1, int(factor_escala))
    for _ in range(intentos_creacion):
        if rand.random() < prob_creacion:
            nuevas_empresas += 1
        
    # Entrada de capital/sucursales extranjeras (depende del tamaño relativo del mercado)
    mercado = presupuesto_promedio_trabajador / estado.presupuesto_referencia if estado.presupuesto_referencia > 0 else 1.0
    prob_entrada = config.tasa_entrada_extranjeras * min(max(mercado, 0.2), 3.0)
    
    # CORRECCIÓN: Los intentos de entrada extranjera escalan con el tamaño de la población de consumidores (mercado potencial)
    intentos_entrada = max(1, int(factor_escala))
    for _ in range(intentos_entrada):
        if rand.random() < prob_entrada:
            nuevas_empresas += 1
        
    # Inicialización e inserción de nuevas empresas
    for _ in range(nuevas_empresas):
        nueva_emp = Empresa.crear_inicial(config, rand)
        nueva_emp.presupuesto = rand.uniform(
            presupuesto_promedio_empresa * 0.75, 
            presupuesto_promedio_empresa * 1.25
        )
        nueva_emp.precio = rand.uniform(
            precio_promedio * 0.75, 
            precio_promedio * 1.25
        )
        nueva_emp.salario = max(
            rand.uniform(salario_promedio * 0.75, salario_promedio * 1.25),
            estado.config.salario_mínimo,
            1.0
        )
        nueva_emp.salario_informal = max(
            rand.uniform(salario_informal_promedio * 0.75, salario_informal_promedio * 1.25),
            1.0
        )
        if trigger:
            nueva_emp.tolerancia = rand.uniform(
                tolerancia_promedio * 0.75, 
                tolerancia_promedio * 1.25
            )
            nueva_emp.productividad_objetivo = rand.uniform(
                productividad_objetivo_promedio * 0.75, 
                productividad_objetivo_promedio * 1.25
            )
            nueva_emp.satisfacción = rand.uniform(
                satisfacción_promedio * 0.75, 
                satisfacción_promedio * 1.25
            )
            nueva_emp.calidad = rand.uniform(
                calidad_promedio * 0.75, 
                calidad_promedio * 1.25
            )
        else:
            nueva_emp.tolerancia = round(rand.uniform(0.0, 1.0), 2)
            nueva_emp.productividad_objetivo = round(rand.uniform(0.1, 1.0), 2)
            nueva_emp.satisfacción = round(rand.uniform(0.0, 1.0), 2)
            nueva_emp.calidad = round(rand.uniform(0.0, 1.0), 2)
        estado.empresas.append(nueva_emp)
        
    # --- Salidas (Cierre y Relocalización) ---
    empresas_activas = []
    for emp in estado.empresas:
        # 1. Quiebra endógena (si se queda sin presupuesto operativo para pagar o pasa mucho tiempo sin vender)
        quiebra_financiera = (emp.presupuesto <= 0 and emp.inventario == 0) or (emp.días_sin_vender > 180)
        
        # 2. Cierre voluntario (adaptativo según tamaño/rentabilidad con respecto al promedio)
        cierre_exogeno = False
        if emp.presupuesto < 0.2 * presupuesto_promedio_empresa:
            cierre_exogeno = rand.random() < 0.05
        
        # 3. Salida por relocalización (exógeno)
        relocalizacion = rand.random() < config.tasa_relocalizacion_empresas
        
        # Si no cumple ninguna de las condiciones de salida, sigue operando
        if not (quiebra_financiera or cierre_exogeno or relocalizacion):
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas