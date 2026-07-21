# --- config.py ---
from dataclasses import dataclass

@dataclass
class Config:

    # Simulación
    semilla: int = 0
    velocidad: float = 0
    frecuencia_actualización: int = 100
    velocidad_streamlit: int = 1

    # Población
    num_trabajadores: int = 1000
    num_empresas: int = 100
    
    # Economía
    presupuesto_inicial: float = 100e2
    precio_inicial: float = 300
    salario_inicial: float = 300
    salario_informal_inicial: float = 50

    # Políticas
    salario_mínimo: float = 0
    salario_mínimo_automático: bool = False
    salario_mínimo_automático_intervalo: int = 30
    salario_mínimo_automático_formalidad_límite: float = 0.0
    salario_mínimo_automático_reducción: float = 0.99
    tasa_salario_mínimo: float = 0.3
    tasa_emisión: float = 0

    # Parámetros del modelo laboral
    reducción_salario: float = 0.99
    aumento_salario: float = 1.01
    informalidad_por_empresa: float = 1.0

    # Parámetros del mercado
    productividad_formal: float = 1
    productividad_informal: float = 0.7
    aumento_precio: float = 1.01
    reducción_precio: float = 0.99