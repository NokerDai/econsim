from dataclasses import dataclass


@dataclass
class Trabajador:
    presupuesto: float = 0

    sensibilidad_calidad: float
    sensibilidad_precio: float