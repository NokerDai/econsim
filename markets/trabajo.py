# --- trabajo.py ---

from models import Contrato


def mercado_laboral(estado):
    salario_máximo = 0

    empresas_formales = []
    vacantes_formales = []

    # 1. Liberar contratos vencidos (aplica tanto a formales como informales)
    for trabajador in estado.trabajadores:
        if trabajador.contrato is not None:
            contrato = trabajador.contrato
            if contrato.vence <= estado.día:
                trabajador.contrato = None

    # 2. Calcular vacantes para el mercado laboral formal
    for empresa in estado.empresas:
        n = int(empresa.presupuesto / empresa.salario)
        if n > 0:
            empresas_formales.append(empresa)
            vacantes_formales.append(n)

    # 3. Contratación en el mercado formal
    for trabajador in estado.trabajadores:
        if trabajador.contrato is None:
            if not empresas_formales:
                break

            i = estado.aleatorio.choices(
                range(len(empresas_formales)),
                weights=vacantes_formales,
                k=1
            )[0]

            empresa = empresas_formales[i]

            trabajador.contrato = Contrato(
                empresa=empresa,
                vence=estado.día + estado.config.duración_contrato,
                tipo="formal"
            )
            
            if empresa.salario > salario_máximo:
                salario_máximo = empresa.salario

            empresa.presupuesto -= empresa.salario
            trabajador.presupuesto += empresa.salario

            nuevo_salario = (
                empresa.salario *
                estado.config.reducción_salario_contratación
            )

            empresa.salario = max(
                nuevo_salario,
                estado.config.salario_mínimo
            )

            vacantes_formales[i] -= 1
            if vacantes_formales[i] == 0:
                vacantes_formales.pop(i)
                empresas_formales.pop(i)

    # Ajustar dinámicamente el salario mínimo si la opción automática está activa
    if estado.config.salario_mínimo_automático and estado.config.salario_mínimo < salario_máximo * estado.config.tasa_salario_mínimo:
        estado.config.salario_mínimo = salario_máximo * estado.config.tasa_salario_mínimo

    # Ajuste de salarios formales por vacantes no cubiertas
    for empresa, vacantes in zip(empresas_formales, vacantes_formales):
        empresa.salario *= (
            estado.config.aumento_salario_vacante ** vacantes
        )

    #### MERCADO INFORMAL ####

    empresas_informales = []
    vacantes_informales = []

    empleados_informales_activos = {empresa: 0 for empresa in estado.empresas}
    for t in estado.trabajadores:
        if t.contrato is not None and t.contrato.tipo == "informal":
            empleados_informales_activos[t.contrato.empresa] += 1

    for empresa in estado.empresas:
        limite_informal = estado.config.informalidad_por_empresa
        activos = empleados_informales_activos[empresa]
        
        if activos < limite_informal:
            n_presupuesto = int(empresa.presupuesto / empresa.salario_informal)
            # El límite de vacantes es la capacidad restante permitida por empresa
            n = min(n_presupuesto, limite_informal - activos)
            if n > 0:
                empresas_informales.append(empresa)
                vacantes_informales.append(n)

    for trabajador in estado.trabajadores:
        if trabajador.contrato is None:
            if not empresas_informales:
                break

            i = estado.aleatorio.choices(
                range(len(empresas_informales)),
                weights=vacantes_informales,
                k=1
            )[0]

            empresa = empresas_informales[i]

            # Creamos un contrato informal
            trabajador.contrato = Contrato(
                empresa=empresa,
                vence=estado.día + estado.config.duración_contrato,
                tipo="informal"
            )

            empresa.presupuesto -= empresa.salario_informal
            trabajador.presupuesto += empresa.salario_informal

            empresa.salario_informal *= estado.config.reducción_salario_contratación

            vacantes_informales[i] -= 1
            if vacantes_informales[i] == 0:
                vacantes_informales.pop(i)
                empresas_informales.pop(i)

    for empresa, vacantes in zip(empresas_informales, vacantes_informales):
        empresa.salario_informal *= (
            estado.config.aumento_salario_vacante ** vacantes
        )