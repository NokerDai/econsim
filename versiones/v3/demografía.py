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
        satisfacción_promedio= sum(e.satisfacción for e in estado.empresas) / num_empresas_actual
        productividad_objetivo_promedio = sum(e.productividad_objetivo for e in estado.empresas) / num_empresas_actual
        tolerancia_promedio = sum(e.tolerancia for e in estado.empresas) / num_empresas_actual
    else:
        # Respaldo a los valores iniciales de config si el mercado se queda sin empresas
        presupuesto_promedio_empresa = config.presupuesto_inicial
        precio_promedio = config.precio_inicial
        salario_promedio = config.salario_inicial
        salario_informal_promedio = config.salario_informal_inicial
        trigger = False

    # ==========================================
    # 2. DINÁMICA DE PERSONAS
    # ==========================================
    
    # --- Entradas (Natalidad e Inmigración) ---
    nuevos_habitantes = 0
    
    # Nacimientos (proporcional al tamaño de la población actual)
    for _ in range(len(estado.trabajadores)):
        if rand.random() < config.tasa_natalidad:
            nuevos_habitantes += 1
            
    # Inmigración (evento externo independiente de la población actual)
    if rand.random() < config.prob_inmigracion:
        nuevos_habitantes += rand.randint(1, config.num_inmigrantes_paso_max)
        
    # Inicialización e inserción de nuevos trabajadores en el estado
    for _ in range(nuevos_habitantes):
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        nuevo_trabajador.presupuesto = rand.uniform(
            presupuesto_promedio_trabajador * 0.75, 
            presupuesto_promedio_trabajador * 1.25
        )
        estado.trabajadores.append(nuevo_trabajador)
        
    # --- Salidas (Mortalidad y Emigración) ---
    sobrevivientes = []
    for t in estado.trabajadores:
        fallece = rand.random() < config.tasa_mortalidad
        emigra = rand.random() < config.tasa_emigracion
        
        # Si no fallece ni emigra, permanece en el sistema
        if not (fallece or emigra):
            sobrevivientes.append(t)
            
    estado.trabajadores = sobrevivientes

    # ==========================================
    # 3. DINÁMICA DE EMPRESAS
    # ==========================================
    
    # --- Entradas (Creación y Entrada Extranjera) ---
    nuevas_empresas = 0
    
    # Emprendimiento local
    if rand.random() < config.tasa_creacion_empresas:
        nuevas_empresas += 1
        
    # Entrada de capital/sucursales extranjeras
    if rand.random() < config.tasa_entrada_extranjeras:
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
            config.salario_mínimo,
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
            nueva_emp.satisfacción = round(rand.uniform(0.0, 1.0), 2),
            nueva_emp.calidad = round(rand.uniform(0.0, 1.0), 2)
        estado.empresas.append(nueva_emp)
        
    # --- Salidas (Cierre y Relocalización) ---
    empresas_activas = []
    for emp in estado.empresas:
        # 1. Quiebra endógena (si se queda sin presupuesto operativo para pagar)
        quiebra_financiera = (emp.presupuesto <= 0 and emp.inventario == 0)
        
        # 2. Cierre administrativo o liquidación voluntaria (exógeno)
        cierre_exogeno = rand.random() < config.tasa_cierre_empresas
        
        # 3. Salida por relocalización (exógeno)
        relocalizacion = rand.random() < config.tasa_relocalizacion_empresas
        
        # Si no cumple ninguna de las condiciones de salida, sigue operando
        if not (quiebra_financiera or cierre_exogeno or relocalizacion):
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas