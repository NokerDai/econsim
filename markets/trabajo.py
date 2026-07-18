from models import Contrato


def mercado_laboral(estado):

    vacantes_diarias = [
        empresa
        for empresa in estado.empresas
        for _ in range(int(min(
            empresa.presupuesto / empresa.salario,
            estado.config.num_trabajadores / estado.config.num_empresas
        )))
    ]

    for trabajador in estado.trabajadores:

        if trabajador.contrato is not None:

            contrato = trabajador.contrato
            empresa = contrato.empresa

            if contrato.vence <= estado.día:

                trabajador.contrato = None

        if trabajador.contrato is None:

            if not vacantes_diarias:
                break

            empresa = estado.aleatorio.choice(vacantes_diarias)

            trabajador.contrato = Contrato(
                empresa=empresa,
                vence=estado.día + estado.config.duración_contrato
            )

            trabajador.presupuesto += empresa.salario

            empresa.presupuesto -= empresa.salario

            nuevo_salario = (
                empresa.salario *
                estado.config.reducción_salario_contratación
            )

            if nuevo_salario >= estado.config.salario_mínimo:
                empresa.salario = nuevo_salario

            vacantes_diarias.remove(empresa)

    for empresa in vacantes_diarias:

        empresa.salario *= estado.config.aumento_salario_vacante