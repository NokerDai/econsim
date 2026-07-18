from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    empleados: int = 0

    stock: int = 0

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other