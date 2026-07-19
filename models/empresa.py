from dataclasses import dataclass

@dataclass
class Empresa:

    presupuesto: float

    precio: float

    salario: float

    salario_informal: float

    vacantes_formales: int = 0

    vacantes_informales: int = 0

    empleados_formales: int = 0

    empleados_informales: int = 0

    inventario: float = 0.0