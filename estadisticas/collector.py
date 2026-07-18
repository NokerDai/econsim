from statistics import mean


def actualizar_estadisticas(estado):

    salarios_formales = [
        empresa.salario
        for empresa in estado.empresas
    ]

    salarios_informales = [
        empresa.salario_informal
        for empresa in estado.empresas
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