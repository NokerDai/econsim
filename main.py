import sys

from PySide6.QtWidgets import QApplication

from config import Config
from simulation import Simulación

from ui.ventana import Ventana


config = Config()


simulación = Simulación(config)


app = QApplication(sys.argv)


ventana = Ventana(simulación)

ventana.show()


sys.exit(
    app.exec()
)