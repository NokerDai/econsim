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

    productividad: float = 0.7

    inventario: float = 0

    inventario_ayer: float = 0

    racha_reducido: int = 0

    racha_aumentado: int = 0

    ventas_hoy: int = 0