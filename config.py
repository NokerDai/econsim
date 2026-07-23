# --- config.py ---
from dataclasses import dataclass

@dataclass
class Config:
    version_modelo: str = "v3"

    # Simulación
    semilla: int = 0
    velocidad: float = 0
    frecuencia_actualización: int = 100
    velocidad_streamlit: int = 1

    # Población
    num_trabajadores: int = 1000
    num_empresas: int = 10
    
    # Economía
    presupuesto_inicial: float = 100000
    precio_inicial: float = 300
    salario_inicial: float = 300
    salario_informal_inicial: float = 50

    # Políticas
    salario_mínimo: float = 0
    salario_mínimo_automático: bool = False
    salario_mínimo_automático_intervalo: int = 30
    salario_mínimo_automático_formalidad_límite: float = 0.0
    salario_mínimo_automático_aumento: float = 1.1
    salario_mínimo_automático_reducción: float = 0.9
    tasa_salario_mínimo: float = 0.3
    tasa_emisión: float = 0
    mantenimiento_M0: bool = True
    mantenimiento_M0_suavizado: int = 3

    # Parámetros del modelo laboral
    poder_trabajadores: float = 0.5
    reducción_salario: float = 0.99
    aumento_salario: float = 1.01
    informalidad_por_empresa: float = 1.0
    sensibilidad_salario: float = 1.0
    sensibilidad_satisfacción: float = 1.0

    # Parámetros del mercado
    productividad_formal: float = 2
    productividad_informal: float = 1.5
    aumento_precio: float = 1.01
    reducción_precio: float = 0.99
    sensibilidad_precio: float = 1.0
    sensibilidad_calidad: float = 1.0

    # Entrada y salida Argentina
    tasa_natalidad = 0.000025          # ≈ 9 nacimientos cada 1000 habitantes/año
    prob_inmigracion = 0.0000012       # probabilidad diaria de evento migratorio
    num_inmigrantes_paso_max = 150.0   # máximo inmigrantes en un paso de simulación
    tasa_emigracion = 0.0000018        # ≈ 0.07 % de la población/año
    tasa_mortalidad = 0.000022         # ≈ 8 muertes cada 1000 habitantes/año
    tasa_creacion_empresas = 0.0000010 # ≈ 0.036 % de empresas nuevas/día
    tasa_entrada_extranjeras = 0.00000004
    tasa_relocalizacion_empresas = 0.0000002