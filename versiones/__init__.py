# versiones/__init__.py
import os

_ruta_actual = os.path.dirname(__file__)

VERSIONES_DISPONIBLES = sorted([
    nombre for nombre in os.listdir(_ruta_actual)
    if os.path.isdir(os.path.join(_ruta_actual, nombre)) and not nombre.startswith("__")
], reverse=True)