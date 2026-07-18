from statistics import mean


def actualizar_estadisticas(estado):

    precio_medio = mean(e.precio for e in estado.empresas)
    salarios_formales = [empresa.salario for empresa in estado.empresas for empleado in range(empresa.empleados_formales)]
    salarios_informales = [empresa.salario_informal for empresa in estado.empresas for empleado in range(empresa.empleados_informales)]
    
    ajuste_formal = 0
    ajuste_informal = 0
    if estado.estadisticas.salario_medio:
        formal = estado.estadisticas.salario_medio[-1]
    if estado.estadisticas.salario_informal_medio:
        informal = estado.estadisticas.salario_informal_medio[-1]

    estado.estadisticas.salario_medio.append(
        mean(salarios_formales) if salarios_formales else ajuste_formal
    )

    estado.estadisticas.salario_informal_medio.append(
        mean(salarios_informales) if salarios_informales else ajuste_informal
    )

    estado.estadisticas.precio_medio.append(
        precio_medio
    )