from dataclasses import dataclass, field


@dataclass
class Estadisticas:

    salario_medio: list = field(default_factory=list)

    salario_informal_medio: list = field(default_factory=list)

    precio_medio: list = field(default_factory=list)


    def mostrar_resumen(self):

        for día, (salario, salario_informal, precio) in enumerate(
            zip(
                self.salario_medio,
                self.salario_informal_medio,
                self.precio_medio
            ),
            start=1
        ):

            if día % 5 == 0:

                print(
                    f"Día {día} | "
                    f"Salario medio: {salario:.2f} | "
                    f"Salario informal medio: {salario_informal:.2f} | "
                    f"Precio medio: {precio:.2f}"
                )