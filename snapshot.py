from dataclasses import dataclass


@dataclass
class Snapshot:

    día: int

    salario_medio: float

    salario_informal_medio: float

    precio_medio: float

    empleo_formal: float

    empleo_informal: float

    desempleo: float

    emisión_diaria: float

    salario_mínimo: float

    salario_mínimo_automático: bool