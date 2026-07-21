from dataclasses import dataclass


@dataclass
class Trabajador:
    sensibilidad_calidad: float
    sensibilidad_precio: float
    presupuesto: float = 0