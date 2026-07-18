from models import Contrato


def mercado_laboral(estado):

    vacantes_diarias = [
        empresa
        for empresa in estado.empresas
        for _ in range(int(
            empresa.presupuesto / empresa.salario))
    ]

    vacantes_informales = []

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
                vence=estado.día + estado.config.duración_contrato,
                tipo="formal"
            )

            trabajador.presupuesto += empresa.salario

            empresa.presupuesto -= empresa.salario

            nuevo_salario = (
                empresa.salario *
                estado.config.reducción_salario_contratación
            )

            if nuevo_salario >= estado.config.salario_mínimo:
                empresa.salario = nuevo_salario
            else:
                empresa.salario = estado.config.salario_mínimo

            vacantes_diarias.remove(empresa)
    
    trabajadores_sin_contrato = [
        trabajador
        for trabajador in estado.trabajadores
        if trabajador.contrato is None
    ]

    if trabajadores_sin_contrato:
        vacantes_informales = [
            empresa
            for empresa in estado.empresas
            for _ in range(int(
                empresa.presupuesto / empresa.salario_informal))
        ]

        for trabajador in trabajadores_sin_contrato:
            if not vacantes_informales:
                break

            empresa = estado.aleatorio.choice(vacantes_informales)

            trabajador.contrato = Contrato(
                empresa=empresa,
                vence=estado.día + estado.config.duración_contrato,
                tipo="informal"
            )

            trabajador.presupuesto += empresa.salario_informal

            empresa.presupuesto -= empresa.salario_informal

            empresa.salario_informal = empresa.salario_informal * estado.config.reducción_salario_contratación

            vacantes_informales.remove(empresa)


    for empresa in vacantes_diarias:

        empresa.salario *= estado.config.aumento_salario_vacante
    
    if trabajadores_sin_contrato:
        for empresa in vacantes_informales:

            empresa.salario_informal *= estado.config.aumento_salario_vacante