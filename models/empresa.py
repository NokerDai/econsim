# --- empresa.py ---

from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    ventas: int = 0

    ventas_anteriores: int = 1000