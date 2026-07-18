from statistics import mean


def actualizar_estadisticas(estado):

    salarios_formales = [
        empresa.salario
        for empresa in estado.empresas
    ]

    estado.estadisticas.salario_medio.append(
        mean(salarios_formales) if salarios_formales else 0.0
    )

    estado.estadisticas.precio_medio.append(
        mean(e.precio for e in estado.empresas)
    )