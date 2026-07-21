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