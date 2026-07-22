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
    num_empresas: int = 100
    
    # Economía
    presupuesto_inicial: float = 10000
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
    mantenimiento_M0_suavizado: int = 10

    # Parámetros del modelo laboral
    peso_trabajador: float = 1.0
    peso_empresa: float = 1.0
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

    # --- Demografía ---
    tasa_natalidad: float = 0.000029               # Probabilidad diaria de nacimiento por habitante
    prob_inmigracion: float = 0.015                # Probabilidad de llegada de inmigrantes un día cualquiera
    num_inmigrantes_paso_max: int = 5              # Cantidad de inmigrantes máxima por suceso
    tasa_mortalidad: float = 0.000023              # Probabilidad diaria de fallecimiento por habitante
    tasa_emigracion: float = 0.000003              # Probabilidad diaria de emigración por habitante

    # --- Ciclo de Vida Empresarial ---
    tasa_creacion_empresas: float = 0.00012        # Probabilidad diaria de creación de una empresa local
    tasa_entrada_extranjeras: float = 0.0004       # Probabilidad de ingreso de una empresa extranjera
    tasa_cierre_empresas: float = 0.00004          # Probabilidad de liquidación exógena por empresa
    tasa_relocalizacion_empresas: float = 0.000005 # Probabilidad de relocalización exógena al extranjero