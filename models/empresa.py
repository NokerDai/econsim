from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    contrató: bool = False

    vendió: bool = False