from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    ventas_mes: int = 0

    ventas_mes_anterior: int = 0