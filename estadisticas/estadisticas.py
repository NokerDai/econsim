# --- estadisticas.py ---
from dataclasses import dataclass, field


@dataclass
class Estadisticas:

    salario_medio: list = field(default_factory=list)

    salario_informal_medio: list = field(default_factory=list)

    precio_lista_medio: list = field(default_factory=list)

    precio_transaccion_medio: list = field(default_factory=list)

    empleo_formal: list = field(default_factory=list)

    empleo_informal: list = field(default_factory=list)

    desempleo: list = field(default_factory=list)

    bienes_vendidos: list = field(default_factory=list)

    calidad_media: list = field(default_factory=list)

    satisfacción_media: list = field(default_factory=list)

    empresas_ingreso: list = field(default_factory=list)

    empresas_gasto: list = field(default_factory=list)