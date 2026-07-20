# --- snapshot.py ---
from dataclasses import dataclass

@dataclass
class Snapshot:
    día: int

    salario_medio: float

    salario_informal_medio: float

    precio_lista_medio: float

    precio_transaccion_medio: float

    empleo_formal: float

    empleo_informal: float

    desempleo: float

    tasa_emisión: float

    salario_mínimo: float

    salario_mínimo_automático: bool

    informalidad_por_empresa: int

    bienes_vendidos: float

    empresas_ingreso: float

    empresas_gasto: float