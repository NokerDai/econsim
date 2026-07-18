from dataclasses import dataclass

@dataclass(eq=False)
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    empleados: int = 0

    stock: int = 0