# --- empresa.py ---

from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    empleados: int = 0

    stock: int = 0

    presupuesto_disponible: float = 0.0

    def __post_init__(self):
        self.presupuesto_disponible = self.presupuesto

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other