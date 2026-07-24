# state.py
from estadisticas import Estadisticas

class Estado:
    def __init__(self, config, EmpresaCls, TrabajadorCls):
        self.config = config
        self.día = 0
        
        import random
        self.aleatorio = random.Random(config.semilla)

        self.trabajadores = [
            TrabajadorCls.crear_inicial(config, self.aleatorio)
            for _ in range(config.num_trabajadores)
        ]

        self.empresas = [
            EmpresaCls.crear_inicial(config, self.aleatorio)
            for _ in range(config.num_empresas)
        ]

        self.estadisticas = Estadisticas()

        self.salario_referencia = float(config.salario_inicial)
        self.salario_informal_referencia = float(config.salario_informal_inicial)
        self.precio_referencia = float(config.precio_inicial)
        self.presupuesto_referencia = float(config.presupuesto_inicial)
        self.beneficio_esperado_referencia = float(1.0)
        self.poder_de_compra_referencia = float(1.0)
        self.presupuesto_referencia_persona = float(1.0)