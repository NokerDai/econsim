from dataclasses import dataclass
from typing import Optional

from .contrato import Contrato


@dataclass
class Trabajador:

    presupuesto: float = 0

    contrato: Optional[Contrato] = None