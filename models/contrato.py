from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .empresa import Empresa


@dataclass
class Contrato:

    empresa: "Empresa"

    vence: int

    tipo: str = "formal"