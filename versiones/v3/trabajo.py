def mercado_laboral(estado):
    vacantes_formales = []

    for empresa in estado.empresas:
        salario_seguro = max(empresa.salario, 1.0)

        empresa.vacantes_formales = min(
            int(empresa.presupuesto / salario_seguro),
            len(estado.trabajadores)
        )

        empresa.vacantes_informales = 0
        empresa.empleados_formales = 0
        empresa.empleados_informales = 0
        empresa.productividad_acumulada_formales = 0.0
        empresa.productividad_acumulada_informales = 0.0

        vacantes_formales.extend([empresa] * empresa.vacantes_formales)

    ssal = estado.config.sensibilidad_salario
    ssat = estado.config.sensibilidad_satisfacción
    rand = estado.aleatorio
    random_func = rand.random

    informalidad = False
    vacantes_informales = []

    salario_formal_máximo = estado.config.salario_mínimo

    for trabajador in estado.trabajadores:

        peso_salario = trabajador.sensibilidad_salario * ssal
        peso_satisfacción = trabajador.sensibilidad_satisfacción * ssat

        # ===========================
        # Mercado formal
        # ===========================

        n_disp = len(vacantes_formales)

        if n_disp > 0:

            k = min(10, n_disp)

            if k == n_disp:
                indices = list(range(n_disp))
            else:
                seen = set()
                indices = []

                while len(indices) < k:
                    idx = int(random_func() * n_disp)
                    if idx not in seen:
                        seen.add(idx)
                        indices.append(idx)

            mejor_indice = -float("inf")
            best_idx_in_list = -1
            seleccionada = None

            alpha = estado.config.poder_trabajadores
            beta = 1.0 - alpha

            for idx in indices:

                emp = vacantes_formales[idx]

                u_trabajador = (
                    peso_salario * emp.salario +
                    peso_satisfacción * emp.satisfacción
                )

                if u_trabajador <= trabajador.utilidad_reserva:
                    continue

                error = abs(
                    trabajador.productividad -
                    emp.productividad_objetivo
                )

                compatibilidad = max(
                    0.0,
                    1.0 - error * (1.0 - emp.tolerancia)
                )

                productividad_real = (
                    trabajador.productividad *
                    compatibilidad
                )

                beneficio = (
                    emp.precio *
                    productividad_real *
                    emp.calidad
                )

                u_empresa = beneficio - emp.salario

                if u_empresa <= 0:
                    continue

                indice = (
                    (u_trabajador - trabajador.utilidad_reserva) ** alpha *
                    (u_empresa ** beta)
                )

                if indice > mejor_indice:
                    mejor_indice = indice
                    seleccionada = emp
                    best_idx_in_list = idx

            if seleccionada is not None:

                seleccionada.empleados_formales += 1
                seleccionada.productividad_acumulada_formales += trabajador.productividad

                trabajador.presupuesto += seleccionada.salario
                seleccionada.presupuesto -= seleccionada.salario

                salario_formal_máximo = max(
                    salario_formal_máximo,
                    seleccionada.salario
                )

                ultimo = len(vacantes_formales) - 1

                if best_idx_in_list != ultimo:
                    vacantes_formales[best_idx_in_list] = vacantes_formales[ultimo]

                vacantes_formales.pop()

                continue

        # ===========================
        # Generar mercado informal
        # ===========================

        if not informalidad:
            informalidad = True

            for empresa in estado.empresas:
                salario_inf_seguro = max(empresa.salario_informal, 1.0)

                empresa.vacantes_informales = min(
                    int(empresa.presupuesto / salario_inf_seguro),
                    len(estado.trabajadores)
                )

                vacantes_informales.extend(
                    [empresa] * empresa.vacantes_informales
                )

        # ===========================
        # Mercado informal
        # ===========================

        n_disp = len(vacantes_informales)

        if n_disp == 0:
            continue

        k = min(10, n_disp)

        if k == n_disp:
            indices = list(range(n_disp))
        else:
            seen = set()
            indices = []

            while len(indices) < k:
                idx = int(random_func() * n_disp)
                if idx not in seen:
                    seen.add(idx)
                    indices.append(idx)

        mejor_indice = -float("inf")
        best_idx_in_list = -1
        seleccionada = None

        alpha = estado.config.poder_trabajadores
        beta = 1.0 - alpha

        for idx in indices:

            emp = vacantes_informales[idx]

            u_trabajador = (
                peso_salario * emp.salario_informal +
                peso_satisfacción * emp.satisfacción
            )

            if u_trabajador <= trabajador.utilidad_reserva:
                continue

            error = abs(
                trabajador.productividad -
                emp.productividad_objetivo
            )

            compatibilidad = max(
                0.0,
                1.0 - error * (1.0 - emp.tolerancia)
            )

            productividad_real = (
                trabajador.productividad *
                compatibilidad
            )

            beneficio = (
                emp.precio *
                productividad_real *
                emp.calidad
            )

            u_empresa = beneficio - emp.salario_informal

            #if u_empresa <= 0:
            #    continue

            indice = (
                (u_trabajador - trabajador.utilidad_reserva) ** alpha *
                (u_empresa ** beta)
            )

            if indice > mejor_indice:
                mejor_indice = indice
                seleccionada = emp
                best_idx_in_list = idx

        if seleccionada is None:
            continue

        seleccionada.empleados_informales += 1
        seleccionada.productividad_acumulada_informales += trabajador.productividad

        trabajador.presupuesto += seleccionada.salario_informal
        seleccionada.presupuesto -= seleccionada.salario_informal

        ultimo = len(vacantes_informales) - 1

        if best_idx_in_list != ultimo:
            vacantes_informales[best_idx_in_list] = vacantes_informales[ultimo]

        vacantes_informales.pop()

    # ===========================
    # Ajustar salarios empresas
    # ===========================

    vacantes_formales_proyectadas = len(estado.trabajadores) / len(estado.empresas)
    num_empleados_formales = sum(
        empresa.empleados_formales
        for empresa in estado.empresas
    )
    num_empleados_informales_proyectados = len(estado.trabajadores) - num_empleados_formales
    vacantes_informales_proyectadas = (num_empleados_informales_proyectados * estado.config.informalidad_por_empresa) / len(estado.empresas)

    # ===========================
    # Actualizar salario mínimo
    # ===========================

    if estado.config.salario_mínimo_automático and estado.día % estado.config.salario_mínimo_automático_intervalo == 0:
        if estado.trabajadores:
            tasa_empleo = num_empleados_formales / len(estado.trabajadores)
        else:
            tasa_empleo = 0.0
        tasa_límite = estado.config.salario_mínimo_automático_formalidad_límite
        reducción = estado.config.salario_mínimo_automático_reducción
        aumento = estado.config.salario_mínimo_automático_aumento

        if estado.config.salario_mínimo == 0:
            estado.config.salario_mínimo = salario_formal_máximo * estado.config.tasa_salario_mínimo * (1 - aumento)
        if tasa_empleo > tasa_límite * 1.05:
            estado.config.salario_mínimo = min(estado.config.salario_mínimo * aumento, salario_formal_máximo * estado.config.tasa_salario_mínimo)
        elif tasa_empleo < tasa_límite * 0.95:
            estado.config.salario_mínimo *= reducción

    for empresa in estado.empresas:
        empresa.salario_pago_real = empresa.salario
        empresa.salario_informal_pago_real = empresa.salario_informal

        ratio = (empresa.vacantes_formales - vacantes_formales_proyectadas) * 0.3
        empresa.salario *= 1 + ratio / 100
        empresa.salario = max(empresa.salario, estado.config.salario_mínimo, 1.0)

        ratio = (empresa.vacantes_informales - vacantes_informales_proyectadas) * 0.3
        empresa.salario_informal *= 1 + ratio / 100
        empresa.salario_informal = max(empresa.salario_informal, 1.0)