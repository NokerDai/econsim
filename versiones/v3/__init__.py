# --- versiones/v3/__init__.py ---
from .dinero import emisión_monetaria
from .productos import mercado_productos
from .trabajo import mercado_laboral
#from .demografía import demografía_y_firmas
from .empresa import Empresa
from .trabajador import Trabajador

__all__ = [
    "emisión_monetaria",
    "mercado_productos",
    "mercado_laboral",
#    "demografía_y_firmas",
    "Empresa",
    "Trabajador"
]