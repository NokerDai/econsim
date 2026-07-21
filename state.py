# --- state.py ---
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

        # Creación de agentes desacoplada mediante métodos factoría
        self.trabajadores = [
            Trabajador.crear_inicial(config, self.aleatorio)
            for _ in range(config.num_trabajadores)
        ]

        self.empresas = [
            Empresa.crear_inicial(config, self.aleatorio)
            for _ in range(config.num_empresas)
        ]

        self.estadisticas = Estadisticas()