from dataclasses import dataclass, field


@dataclass
class Estadisticas:

    salario_medio: list = field(default_factory=list)

    precio_medio: list = field(default_factory=list)