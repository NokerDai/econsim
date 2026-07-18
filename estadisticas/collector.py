from statistics import mean


def actualizar_estadisticas(estado):

    precio_medio = mean(e.precio for e in estado.empresas)
    salarios_formales = [trabajador.salario for trabajador in estado.trabajadores if trabajador.trabajo == 1]
    salarios_informales = [trabajador.salario for trabajador in estado.trabajadores if trabajador.trabajo == 2]

    estado.estadisticas.salario_medio.append(
        mean(salarios_formales) if salarios_formales else 0.0
    )

    estado.estadisticas.salario_informal_medio.append(
        mean(salarios_informales) if salarios_informales else 0.0
    )

    estado.estadisticas.precio_medio.append(
        precio_medio
    )