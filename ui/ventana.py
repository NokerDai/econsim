from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QSlider,
)

from PySide6.QtCore import Qt, Signal

from ui.grafico import Grafico


class Ventana(QWidget):

    snapshot_received = Signal(object)

    def __init__(self, simulación):

        super().__init__()

        self.simulación = simulación


        self.setWindowTitle(
            "Simulación económica"
        )

        self.resize(
            900,
            600
        )


        layout = QVBoxLayout()


        self.día_label = QLabel(
            "Día: 0"
        )


        self.boton_iniciar = QPushButton(
            "Iniciar"
        )

        self.boton_pausar = QPushButton(
            "Pausar"
        )

        self.boton_paso = QPushButton(
            "Día siguiente"
        )


        self.slider_emisión = QSlider(
            Qt.Horizontal
        )

        self.slider_emisión.setRange(
            0,
            100000
        )

        self.salario_label = QLabel(
            f"Salario mínimo: {self.simulación.config.salario_mínimo}"
        )

        self.slider_salario = QSlider(
            Qt.Horizontal
        )

        self.slider_salario.setRange(
            0,
            10000
        )

        self.slider_salario.setValue(
            int(self.simulación.config.salario_mínimo)
        )

        self.grafico = Grafico()

        self.snapshot_received.connect(self.actualizar)

        layout.addWidget(
            self.día_label
        )

        layout.addWidget(
            self.boton_iniciar
        )

        layout.addWidget(
            self.boton_pausar
        )

        layout.addWidget(
            self.boton_paso
        )

        layout.addWidget(
            self.salario_label
        )

        layout.addWidget(
            self.slider_salario
        )

        layout.addWidget(
            self.slider_emisión
        )

        layout.addWidget(
            self.grafico
        )


        self.setLayout(layout)


        self.conectar()


    def conectar(self):

        self.boton_iniciar.clicked.connect(
            self.simulación.iniciar
        )


        self.boton_pausar.clicked.connect(
            self.simulación.pausar
        )


        self.boton_paso.clicked.connect(
            self.simulación.step
        )


        self.slider_emisión.valueChanged.connect(
            self.cambiar_emisión
        )

        self.slider_salario.valueChanged.connect(
            self.cambiar_salario
        )

        self.simulación.agregar_callback(
            self.snapshot_received.emit
        )


    def cambiar_emisión(self, valor):

        self.simulación.cambiar_emisión(
            valor
        )


    def cambiar_salario(self, valor):

        self.simulación.cambiar_salario_mínimo(
            valor
        )

        self.salario_label.setText(
            f"Salario mínimo: {valor}"
        )


    def actualizar(self, snapshot):

        self.día_label.setText(
            f"Día: {snapshot.día}"
        )

        self.grafico.actualizar(
            snapshot
        )