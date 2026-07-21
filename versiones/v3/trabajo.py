# --- trabajo.py ---

def mercado_laboral(estado):
    vacantes_formales = []

    for empresa in estado.empresas:
        salario_seguro = max(empresa.salario, 1.0)

        empresa.vacantes_formales = min(
            int(empresa.presupuesto / salario_seguro),
            estado.config.num_trabajadores
        )
        empresa.vacantes_informales = 0
        empresa.empleados_formales = 0
        empresa.empleados_informales = 0

        vacantes_formales.extend([empresa] * empresa.vacantes_formales)

    ssal = estado.config.sensibilidad_salario
    ssat = estado.config.sensibilidad_satisfacción
    rand = estado.aleatorio
    random_func = rand.random  # Acceso directo al generador en C, mucho más rápido

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

            # 1. Muestreo de k índices únicos ultra rápido (Rejection Sampling)
            if k == n_disp:
                indices = list(range(n_disp))
            else:
                seen = set()
                indices = []
                for _ in range(k):
                    idx = int(random_func() * n_disp)
                    while idx in seen:
                        idx = int(random_func() * n_disp)
                    seen.add(idx)
                    indices.append(idx)

            # 2. Búsqueda de la mejor empresa (mayor salario y satisfacción, ponderados)
            best_idx_in_list = -1
            best_score = -float('inf')
            seleccionada = None

            for idx in indices:
                emp = vacantes_formales[idx]
                u_empleado = emp.salario * peso_salario + emp.satisfacción * peso_satisfacción
                u_empresa = trabajador.productividad * emp.exigencia / emp.salario
                score = u_empleado + u_empresa
                if score > best_score:
                    best_score = score
                    best_idx_in_list = idx
                    seleccionada = emp

            seleccionada.empleados_formales += 1

            trabajador.presupuesto += seleccionada.salario
            seleccionada.presupuesto -= seleccionada.salario

            salario_formal_máximo = max(salario_formal_máximo, seleccionada.salario)

            # 3. Eliminación O(1) con swap-and-pop
            last_idx = len(vacantes_formales) - 1
            if best_idx_in_list != last_idx:
                vacantes_formales[best_idx_in_list] = vacantes_formales[last_idx]
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
                    estado.config.num_trabajadores
                )
                vacantes_informales.extend([empresa] * empresa.vacantes_informales)

        # ===========================
        # Mercado informal
        # ===========================

        n_disp = len(vacantes_informales)

        if n_disp > 0:
            k = min(10, n_disp)

            if k == n_disp:
                indices = list(range(n_disp))
            else:
                seen = set()
                indices = []
                for _ in range(k):
                    idx = int(random_func() * n_disp)
                    while idx in seen:
                        idx = int(random_func() * n_disp)
                    seen.add(idx)
                    indices.append(idx)

            best_idx_in_list = -1
            best_score = -float('inf')
            seleccionada = None

            for idx in indices:
                emp = vacantes_informales[idx]
                u_empleado = emp.salario_informal * peso_salario + emp.satisfacción * peso_satisfacción
                u_empresa = trabajador.productividad * emp.exigencia / emp.salario_informal
                score = u_empleado + u_empresa
                if score > best_score:
                    best_score = score
                    best_idx_in_list = idx
                    seleccionada = emp

            seleccionada.empleados_informales += 1

            trabajador.presupuesto += seleccionada.salario_informal
            seleccionada.presupuesto -= seleccionada.salario_informal

            last_idx = len(vacantes_informales) - 1
            if best_idx_in_list != last_idx:
                vacantes_informales[best_idx_in_list] = vacantes_informales[last_idx]
            vacantes_informales.pop()

    # ===========================
    # Ajustar salarios empresas
    # ===========================

    vacantes_formales_proyectadas = estado.config.num_trabajadores / estado.config.num_empresas
    num_empleados_formales = sum([empresa.empleados_formales for empresa in estado.empresas])
    num_empleados_informales_proyectados = estado.config.num_trabajadores - num_empleados_formales
    vacantes_informales_proyectadas = (num_empleados_informales_proyectados * estado.config.informalidad_por_empresa) / estado.config.num_empresas

    # ===========================
    # Actualizar salario mínimo
    # ===========================

    if estado.config.salario_mínimo_automático and estado.día % estado.config.salario_mínimo_automático_intervalo == 0:
        tasa_empleo = num_empleados_formales / estado.config.num_trabajadores
        tasa_límite = estado.config.salario_mínimo_automático_formalidad_límite
        reducción = estado.config.salario_mínimo_automático_reducción
        aumento = estado.config.salario_mínimo_automático_aumento
        if tasa_empleo > tasa_límite * 1.05:
            if estado.config.salario_mínimo > 1:
                estado.config.salario_mínimo = min(estado.config.salario_mínimo * aumento, salario_formal_máximo * estado.config.tasa_salario_mínimo)
            else:
                estado.config.salario_mínimo = salario_formal_máximo * estado.config.tasa_salario_mínimo * reducción
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