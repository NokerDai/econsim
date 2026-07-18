from dataclasses import dataclass


@dataclass
class Snapshot:

    día: int

    salario_medio: float

    salario_informal_medio: float

    precio_medio: float

    tasa_emisión: float

    salario_mínimo: float

    salario_mínimo_automático: bool

    informalidad_por_empresa: int