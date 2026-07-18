from collections import deque

def mercado_laboral(estado):
    vacantes_formales = []

    # Generar vacantes formales
    for empresa in estado.empresas:
        empresa.vacantes_formales = int(empresa.presupuesto / empresa.salario)
        empresa.vacantes_informales = 0
        empresa.empleados_formales = 0
        empresa.empleados_informales = 0

        vacantes_formales.extend([empresa] * empresa.vacantes_formales)

    vacantes_formales.sort(key=lambda e: e.salario, reverse=True)
    vacantes_formales = deque(vacantes_formales)

    informalidad = False
    vacantes_informales = deque()

    salario_formal_máximo = estado.config.salario_mínimo

    for trabajador in estado.trabajadores:

        # ===========================
        # Mercado formal
        # ===========================

        if vacantes_formales:
            seleccionada = vacantes_formales.popleft()

            seleccionada.empleados_formales += 1

            trabajador.presupuesto += seleccionada.salario
            seleccionada.presupuesto -= seleccionada.salario

            salario_formal_máximo = max(
                salario_formal_máximo,
                seleccionada.salario
            )

            continue

        # ===========================
        # Generar mercado informal
        # ===========================

        if not informalidad:
            informalidad = True

            vacantes = []

            for empresa in estado.empresas:

                if empresa.salario_informal != 0:
                    n = empresa.presupuesto / empresa.salario_informal
                else:
                    n = estado.config.informalidad_por_empresa

                empresa.vacantes_informales = int(
                    min(
                        estado.config.informalidad_por_empresa,
                        n
                    )
                )

                vacantes.extend(
                    [empresa] * empresa.vacantes_informales
                )

            # Orden correcto
            vacantes.sort(
                key=lambda e: e.salario_informal,
                reverse=True
            )

            vacantes_informales = deque(vacantes)

        # ===========================
        # Mercado informal
        # ===========================

        if vacantes_informales:
            seleccionada = vacantes_informales.popleft()

            seleccionada.empleados_informales += 1

            trabajador.presupuesto += seleccionada.salario_informal
            seleccionada.presupuesto -= seleccionada.salario_informal

    # ===========================
    # Actualizar salario mínimo
    # ===========================

    if estado.config.salario_mínimo_automático:
        estado.config.salario_mínimo = (
            salario_formal_máximo *
            estado.config.tasa_salario_mínimo
        )

    # ===========================
    # Ajustar salarios empresas
    # ===========================

    vacantes_promedio = (
        estado.config.num_trabajadores /
        estado.config.num_empresas
    )

    sensibilidad = 0.1

    for empresa in estado.empresas:

        ratio = empresa.vacantes_formales / vacantes_promedio
        empresa.salario *= ratio ** sensibilidad
        empresa.salario = max(
            empresa.salario,
            estado.config.salario_mínimo
        )

        if empresa.vacantes_informales > 0:
            ratio = empresa.vacantes_informales / vacantes_promedio
            empresa.salario_informal *= ratio ** sensibilidad