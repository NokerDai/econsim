# --- empresa.py ---
from dataclasses import dataclass

@dataclass
class Empresa:
    presupuesto: float
    precio: float

    calidad: float
    satisfacción: float

    salario: float
    salario_informal: float

    exigencia: float

    precio_venta_real: float = 0.0
    salario_pago_real: float = 0.0
    salario_informal_pago_real: float = 0.0

    vacantes_formales: int = 0
    vacantes_informales: int = 0

    empleados_formales: int = 0
    empleados_informales: int = 0

    productividad: float = 0.7

    inventario: float = 0.0
    inventario_ayer: float = 0.0

    racha_reducido: int = 0
    racha_aumentado: int = 0

    ventas_hoy: int = 0

    @classmethod
    def crear_inicial(cls, config, aleatorio):
        """
        Método de fábrica para construir una Empresa con sus 
        valores iniciales correspondientes de forma encapsulada.
        """
        return cls(
            presupuesto=config.presupuesto_inicial,
            precio=config.precio_inicial,
            calidad=round(aleatorio.uniform(0.5, 1.5), 2),
            satisfacción=round(aleatorio.uniform(0.5, 1.5), 2),
            exigencia=round(aleatorio.uniform(0.5, 1.5), 2),
            salario=config.salario_inicial,
            salario_informal=config.salario_informal_inicial
        )