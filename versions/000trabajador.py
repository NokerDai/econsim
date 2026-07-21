# --- trabajador.py ---
from dataclasses import dataclass

@dataclass
class Trabajador:
    sensibilidad_precio: float
    sensibilidad_calidad: float
    presupuesto: float = 0.0

    @classmethod
    def crear_inicial(cls, config, aleatorio):
        """
        Método de fábrica para construir un Trabajador con sus 
        valores iniciales correspondientes de forma encapsulada.
        """
        return cls(
            presupuesto=0.0,
            sensibilidad_precio=0.0,
            sensibilidad_calidad=0.0
        )