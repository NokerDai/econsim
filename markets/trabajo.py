# --- trabajo.py ---
from collections import deque

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

            salario_formal_máximo = max(salario_formal_máximo, seleccionada.salario)

            continue

        # ===========================
        # Generar mercado informal
        # ===========================

        if not informalidad:
            informalidad = True

            vacantes = []

            for empresa in estado.empresas:
                salario_inf_seguro = max(empresa.salario_informal, 1.0)
                
                empresa.vacantes_informales = min(
                    int(empresa.presupuesto / salario_inf_seguro),
                    estado.config.num_trabajadores
                )
                vacantes.extend([empresa] * empresa.vacantes_informales)

            vacantes.sort(key=lambda e: e.salario_informal, reverse=True)

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

    if estado.config.salario_mínimo_automático and estado.día % estado.config.salario_mínimo_automático_intervalo == 0:
        estado.config.salario_mínimo = (salario_formal_máximo * estado.config.tasa_salario_mínimo)

    # ===========================
    # Ajustar salarios empresas
    # ===========================

    vacantes_formales_proyectadas = estado.config.num_trabajadores / estado.config.num_empresas
    num_empleados_formales = sum([empresa.empleados_formales for empresa in estado.empresas])
    num_empleados_informales_proyectados = estado.config.num_trabajadores - num_empleados_formales
    vacantes_informales_proyectadas = (num_empleados_informales_proyectados * estado.config.informalidad_por_empresa) / estado.config.num_empresas

    for empresa in estado.empresas:
        empresa.salario_pago_real = empresa.salario
        empresa.salario_informal_pago_real = empresa.salario_informal

        ratio = empresa.vacantes_formales - vacantes_formales_proyectadas
        empresa.salario *= 1 + ratio / 100
        empresa.salario = max(empresa.salario, estado.config.salario_mínimo, 1.0)

        ratio = empresa.vacantes_informales - vacantes_informales_proyectadas
        empresa.salario_informal *= 1 + ratio / 100
        empresa.salario_informal = max(empresa.salario_informal, 1.0)