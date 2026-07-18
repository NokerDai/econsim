# --- config.py ---
from dataclasses import dataclass


@dataclass
class Config:

    # Simulación
    semilla: int = 0
    días: int = 100000
    velocidad: float = 0.01
    frecuencia_actualización: int = 100

    # Población
    num_trabajadores: int = 1000
    num_empresas: int = 100
    
    # Economía
    presupuesto_inicial: float = 100e2
    precio_inicial: float = 300
    salario_inicial: float = 300
    salario_informal_inicial: float = 200

    # Políticas
    salario_mínimo: float = 0
    salario_mínimo_automático: bool = False
    tasa_salario_mínimo: float = 1.0
    tasa_emisión: float = 1

    # Parámetros del modelo laboral
    duración_contrato: int = 30
    reducción_salario_contratación: float = 0.99
    reducción_salario_renovación: float = 0.99
    aumento_salario_vacante: float = 1.01
    informalidad_por_empresa: int = 100

    # Parámetros del mercado
    período_actualización_precios: int = 30
    aumento_precio: float = 1.01
    reducción_precio: float = 0.99