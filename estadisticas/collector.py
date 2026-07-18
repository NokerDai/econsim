from statistics import mean


def actualizar_estadisticas(estado):

    precio_medio = mean(e.precio for e in estado.empresas)
    salarios_formales = [empresa.salario for empresa in estado.empresas for empleado in range(empresa.empleados_formales)]
    salarios_informales = [empresa.salario_informal for empresa in estado.empresas for empleado in range(empresa.empleados_informales)]

    estado.estadisticas.salario_medio.append(
        mean(salarios_formales) if salarios_formales else 0.0
    )

    estado.estadisticas.salario_informal_medio.append(
        mean(salarios_informales) if salarios_informales else 0.0
    )

    estado.estadisticas.precio_medio.append(
        precio_medio
    )