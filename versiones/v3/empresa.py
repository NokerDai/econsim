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

    productividad_objetivo: float
    tolerancia: float
    utilidad_reserva: float = 0.0

    días_sin_vender: int = 0

    precio_venta_real: float = 0.0
    salario_pago_real: float = 0.0
    salario_informal_pago_real: float = 0.0

    vacantes_formales: int = 0
    vacantes_informales: int = 0

    empleados_formales: int = 0
    empleados_informales: int = 0

    productividad: float = 0.7
    productividad_acumulada_formales: float = 0.0
    productividad_acumulada_informales: float = 0.0

    inventario: float = 0.0
    inventario_ayer: float = 0.0
    producción: float = 0.0

    racha_reducido: int = 0
    racha_aumentado: int = 0

    ventas_hoy: int = 0

    beneficio_esperado: float = 0.0

    probabilidad_venta_esperada: float = 1.0
    producción_esperada: float = 0.0

    ingresos_esperados: float = 0.0
    salarios_esperados: float = 0.0
    otros_costos_esperados: float = 0.0

    @classmethod
    def crear_inicial(cls, config, aleatorio):
        """
        Método de fábrica para construir una Empresa con sus 
        valores iniciales correspondientes de forma encapsulada.
        """
        return cls(
            presupuesto=config.presupuesto_inicial,
            precio=config.precio_inicial,
            calidad=round(aleatorio.uniform(0.0, 1.0), 2),
            satisfacción=round(aleatorio.uniform(0.0, 1.0), 2),
            productividad_objetivo=round(aleatorio.uniform(0.0, 1.0), 2),
            tolerancia=round(aleatorio.uniform(0.0, 1.0), 2),
            salario=config.salario_inicial,
            salario_informal=config.salario_informal_inicial
        )