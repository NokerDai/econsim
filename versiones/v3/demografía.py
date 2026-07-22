# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    
    # ==========================================
    # 1. DINÁMICA DE PERSONAS
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
    # 2. DINÁMICA DE EMPRESAS
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
        estado.empresas.append(nueva_emp)
        
    # --- Salidas (Cierre y Relocalización) ---
    empresas_activas = []
    for emp in estado.empresas:
        # 1. Quiebra endógena (si se queda sin presupuesto operativo para pagar)
        quiebra_financiera = emp.presupuesto <= 0 and emp.inventario == 0
        
        # 2. Cierre administrativo o liquidación voluntaria (exógeno)
        cierre_exogeno = rand.random() < config.tasa_cierre_empresas
        
        # 3. Salida por relocalización (exógeno)
        relocalizacion = rand.random() < config.tasa_relocalizacion_empresas
        
        # Si no cumple ninguna de las condiciones de salida, sigue operando
        if not (quiebra_financiera or cierre_exogeno or relocalizacion):
            empresas_activas.append(emp)
            
    estado.empresas = empresas_activas