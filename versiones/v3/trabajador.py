# --- trabajador.py ---
from dataclasses import dataclass

@dataclass
class Trabajador:
    sensibilidad_precio: float
    sensibilidad_calidad: float
    sensibilidad_estabilidad: float
    sensibilidad_seguridad: float
    sensibilidad_salario: float
    presupuesto: float = 0.0

    @classmethod
    def crear_inicial(cls, config, aleatorio):
        """
        Método de fábrica para construir un Trabajador con sus 
        valores iniciales correspondientes de forma encapsulada.
        """
        return cls(
            sensibilidad_precio=round(aleatorio.uniform(0.0, 2.0), 2),
            sensibilidad_calidad=round(aleatorio.uniform(0.0, 2.0), 2),
            sensibilidad_estabilidad=round(aleatorio.uniform(0.0, 2.0), 2),
            sensibilidad_seguridad=round(aleatorio.uniform(0.0, 2.0), 2),
            sensibilidad_salario=round(aleatorio.uniform(0.0, 2.0), 2),
            presupuesto=0.0
        )