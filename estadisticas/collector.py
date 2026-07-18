from statistics import mean


def actualizar_estadisticas(estado):

    salarios_formales = [
        trabajador.contrato.empresa.salario
        for trabajador in estado.trabajadores
        if trabajador.contrato is not None and trabajador.contrato.tipo == "formal"
    ]

    salarios_informales = [
        trabajador.contrato.empresa.salario_informal
        for trabajador in estado.trabajadores
        if trabajador.contrato is not None and trabajador.contrato.tipo == "informal"
    ]

    estado.estadisticas.salario_medio.append(
        mean(salarios_formales) if salarios_formales else 0.0
    )

    estado.estadisticas.salario_informal_medio.append(
        mean(salarios_informales) if salarios_informales else 0.0
    )

    estado.estadisticas.precio_medio.append(
        mean(e.precio for e in estado.empresas)
    )