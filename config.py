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
    productividad_informal: float = 2
    aumento_precio: float = 1.01
    reducción_precio: float = 0.99
    sensibilidad_precio: float = 1.0
    sensibilidad_calidad: float = 1.0

    tasa_natalidad: float = 0.0000210 * 100
    prob_inmigracion: float = 0.0000015 * 100
    tasa_emigracion: float = 0.0000015 * 100
    tasa_mortalidad: float = 0.0000210 * 100

    tasa_creacion_empresas: float = 0.00000025 * 100
    tasa_entrada_extranjeras: float = 0.00000015 * 100
    tasa_relocalizacion_empresas: float = 0.00000040 * 100