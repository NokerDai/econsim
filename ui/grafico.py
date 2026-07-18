import pyqtgraph as pg

from PySide6.QtWidgets import QWidget, QVBoxLayout


class Grafico(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.plot = pg.PlotWidget()

        self.plot.setLabel(
            "bottom",
            "Día"
        )

        self.plot.setLabel(
            "left",
            "Valor"
        )

        self.curva_salario = self.plot.plot(
            pen="y",
            name="Salario"
        )

        self.curva_precio = self.plot.plot(
            pen="r",
            name="Precio"
        )


        layout.addWidget(self.plot)

        self.setLayout(layout)


        self.días = []
        self.salarios = []
        self.precios = []


    def actualizar(self, snapshot):

        self.días.append(snapshot.día)

        self.salarios.append(
            snapshot.salario_medio
        )

        self.precios.append(
            snapshot.precio_medio
        )

        # Mantener solo el historial de los últimos 365 días
        if len(self.días) > 365:
            self.días = self.días[-365:]
            self.salarios = self.salarios[-365:]
            self.precios = self.precios[-365:]

        self.curva_salario.setData(
            self.días,
            self.salarios
        )

        self.curva_precio.setData(
            self.días,
            self.precios
        )

        if self.días:
            último_día = self.días[-1]
            inicio = max(0, último_día - 364)
            self.plot.setXRange(inicio, último_día, padding=0)
