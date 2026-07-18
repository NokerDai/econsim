# --- collector.py ---
def actualizar_estadisticas(estado):
    total_empresas = len(estado.empresas)
    precio_medio = sum(e.precio for e in estado.empresas) / total_empresas if total_empresas > 0 else 0.0

    # Evitamos generar listas expandidas usando sumas ponderadas directamente
    num_formales = sum(e.empleados_formales for e in estado.empresas)
    suma_salarios_formales = sum(e.salario * e.empleados_formales for e in estado.empresas)

    num_informales = sum(e.empleados_informales for e in estado.empresas)
    suma_salarios_informales = sum(e.salario_informal * e.empleados_informales for e in estado.empresas)

    estado.estadisticas.salario_medio.append(
        suma_salarios_formales / num_formales if num_formales > 0 else 0.0
    )

    estado.estadisticas.salario_informal_medio.append(
        suma_salarios_informales / num_informales if num_informales > 0 else 0.0
    )

    estado.estadisticas.precio_medio.append(precio_medio)

    total_trabajadores = estado.config.num_trabajadores
    tasa_formal = num_formales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_informal = num_informales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_desempleo = max(0.0, 1.0 - tasa_formal - tasa_informal)

    estado.estadisticas.empleo_formal.append(tasa_formal)
    estado.estadisticas.empleo_informal.append(tasa_informal)
    estado.estadisticas.desempleo.append(tasa_desempleo)