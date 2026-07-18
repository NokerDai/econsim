# --- collector.py ---
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

    num_formales = sum(e.empleados_formales for e in estado.empresas)
    num_informales = sum(e.empleados_informales for e in estado.empresas)
    total_trabajadores = estado.config.num_trabajadores

    tasa_formal = num_formales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_informal = num_informales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_desempleo = max(0.0, 1.0 - tasa_formal - tasa_informal)

    estado.estadisticas.empleo_formal.append(tasa_formal)
    estado.estadisticas.empleo_informal.append(tasa_informal)
    estado.estadisticas.desempleo.append(tasa_desempleo)