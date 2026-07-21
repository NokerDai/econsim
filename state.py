import random

from models import Trabajador, Empresa
from estadisticas import Estadisticas


class Estado:

    def __init__(self, config):

        self.config = config

        # Tiempo
        self.día = 0

        # Aleatoriedad
        self.aleatorio = random.Random(config.semilla)

        # Agentes
        self.trabajadores = [
            Trabajador()
            for _ in range(config.num_trabajadores)
        ]

        self.empresas = [
            Empresa(
                presupuesto=config.presupuesto_inicial,
                precio=config.precio_inicial,
                salario=config.salario_inicial,
                salario_informal=config.salario_informal_inicial
            )
            for _ in range(config.num_empresas)
        ]

        self.estadisticas = Estadisticas()