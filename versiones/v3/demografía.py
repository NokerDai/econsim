# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    
    # ==========================================
    # 1. CÁLCULO DE PROMEDIOS EN TIEMPO REAL
    # ==========================================
    poblacion_actual = len(estado.trabajadores)
    if poblacion_actual > 0:
        presupuesto_promedio_trabajador = sum(t.presupuesto for t in estado.trabajadores) / poblacion_actual
    else:
        presupuesto_promedio_trabajador = 0.0

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
        presupuesto_promedio_empresa = estado.presupuesto_referencia
        precio_promedio = estado.precio_referencia
        salario_promedio = estado.salario_referencia
        salario_informal_promedio = estado.salario_informal_referencia
        trigger = False

    # Promedio móvil exponencial (EMA) para adaptar referencias lentamente (365 días)
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
    poblacion_referencia = getattr(config, 'num_trabajadores', 100.0)
    factor_escala = max(1.0, poblacion_actual / poblacion_referencia)

    # ==========================================
    # 2. DINÁMICA DE PERSONAS
    # ==========================================
    
    # Cálculo de tasas de empleo y desempleo
    num_formales = sum(e.empleados_formales for e in estado.empresas)
    num_informales = sum(e.empleados_informales for e in estado.empresas)
    if poblacion_actual > 0:
        tasa_formal = num_formales / poblacion_actual
        tasa_informal = num_informales / poblacion_actual
        tasa_desempleo = max(0.0, 1.0 - tasa_formal - tasa_informal)
    else:
        tasa_desempleo = 0.0

    tasa_empleo = 1.0 - tasa_desempleo

    # --- Entradas (Natalidad e Inmigración sensibles al contexto) ---
    nuevos_habitantes = 0
    
    # Poder de compra real
    div_referencia = estado.presupuesto_referencia_persona / estado.precio_referencia if estado.precio_referencia * estado.presupuesto_referencia_persona > 0 else 1.0
    poder_de_compra = (presupuesto_promedio_trabajador / precio_promedio) / div_referencia if precio_promedio > 0 else 1.0
    
    # El factor de estrés reduce la natalidad e inmigración si hay desempleo masivo
    factor_estres_economico = max(0.1, tasa_empleo) 
    
    tasa_natalidad_dinamica = config.tasa_natalidad * min(max(poder_de_compra, 0.5), 2.0) * factor_estres_economico
    prob_inmigracion_dinamica = config.prob_inmigracion * min(max(poder_de_compra, 0.5), 2.0) * factor_estres_economico
    
    # Intentos de natalidad
    for _ in range(poblacion_actual):
        if rand.random() < tasa_natalidad_dinamica:
            nuevos_habitantes += 1
            
    # Intentos de inmigración (escalados con el tamaño del mercado)
    intentos_inmigracion = max(1, int(factor_escala))
    for _ in range(intentos_inmigracion):
        if rand.random() < prob_inmigracion_dinamica:
            nuevos_habitantes += 1
        
    for _ in range(nuevos_habitantes):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        nuevo_trabajador.presupuesto = rand.uniform(
            presupuesto_promedio_trabajador * 0.75, 
            presupuesto_promedio_trabajador * 1.25
        ) if presupuesto_promedio_trabajador > 0 else 0.0
        estado.trabajadores.append(nuevo_trabajador)
        
    # --- Salidas (Mortalidad Dinámica y Emigración No Lineal) ---
    # La emigración reacciona exponencialmente ante el desempleo para balancear el mercado sin requerir muertes
    tasa_emigracion_dinamica = config.tasa_emigracion * (1.0 + 8.0 * (tasa_desempleo ** 2))
    
    sobrevivientes = []
    for t in estado.trabajadores:
        # Inanición gradual: El riesgo de fallecer se incrementa de forma cuadrática a partir del día 10 sin comprar
        prob_inanicion = 0.0
        if t.días_sin_comprar > 10:
            prob_inanicion = min(0.95, ((t.días_sin_comprar - 10) ** 2) / 400.0) # ~10% al día 20, ~40% al día 30
            
        fallece = rand.random() < (config.tasa_mortalidad + prob_inanicion)
        emigra = rand.random() < tasa_emigracion_dinamica
        
        if not (fallece or emigra):
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes

    # ==========================================
    # 3. DINÁMICA DE EMPRESAS
    # ==========================================
    nuevas_empresas = 0
    
    # Creación basada en la rentabilidad comparada con el histórico
    rentabilidad = presupuesto_promedio_empresa / estado.presupuesto_referencia if estado.presupuesto_referencia > 0 else 1.0
    prob_creacion = config.tasa_creacion_empresas * min(max(rentabilidad, 0.2), 3.0)
    
    intentos_creacion = max(1, int(factor_escala))
    for _ in range(intentos_creacion):
        if rand.random() < prob_creacion:
            nuevas_empresas += 1
        
    # Entrada extranjera (ligada al poder de compra de los consumidores)
    prob_entrada = config.tasa_entrada_extranjeras * min(max(poder_de_compra, 0.2), 3.0)
    
    intentos_entrada = max(1, int(factor_escala))
    for _ in range(intentos_entrada):
        if rand.random() < prob_entrada:
            nuevas_empresas += 1
        
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
            nueva_emp.tolerancia = rand.uniform(tolerancia_promedio * 0.75, tolerancia_promedio * 1.25)
            nueva_emp.productividad_objetivo = rand.uniform(productividad_objetivo_promedio * 0.75, productividad_objetivo_promedio * 1.25)
            nueva_emp.satisfacción = rand.uniform(satisfacción_promedio * 0.75, satisfacción_promedio * 1.25)
            nueva_emp.calidad = rand.uniform(calidad_promedio * 0.75, calidad_promedio * 1.25)
        else:
            nueva_emp.tolerancia = round(rand.uniform(0.0, 1.0), 2)
            nueva_emp.productividad_objetivo = round(rand.uniform(0.1, 1.0), 2)
            nueva_emp.satisfacción = round(rand.uniform(0.0, 1.0), 2)
            nueva_emp.calidad = round(rand.uniform(0.0, 1.0), 2)
        estado.empresas.append(nueva_emp)
        
    # --- Salidas (Cierre y Relocalización) ---
    empresas_activas = []
    
    # Umbral de cierre voluntario que mezcla el promedio actual y la referencia histórica 
    # para evitar que las empresas moribundas se vuelvan "zombis" en recesiones generales.
    benchmark_cierre = 0.2 * (presupuesto_promedio_empresa * 0.3 + estado.presupuesto_referencia * 0.7)
    
    for emp in estado.empresas:
        quiebra_financiera = (emp.presupuesto <= 0 and emp.inventario == 0) or (emp.días_sin_vender > 180)
        
        cierre_exogeno = False
        if emp.presupuesto < benchmark_cierre:
            cierre_exogeno = rand.random() < 0.08  # Probabilidad ligeramente superior para depurar el mercado
        
        relocalizacion = rand.random() < config.tasa_relocalizacion_empresas
        
        if not (quiebra_financiera or cierre_exogeno or relocalizacion):
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas