from statistics import mean


def actualizar_estadisticas(estado):

    estado.estadisticas.salario_medio.append(
        mean(e.salario for e in estado.empresas)
    )

    estado.estadisticas.precio_medio.append(
        mean(e.precio for e in estado.empresas)
    )