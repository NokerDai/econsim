from models import Contrato


def mercado_laboral(estado):
    salario_máximo = 0

    empresas_formales = []
    vacantes_formales = []

    for empresa in estado.empresas:
        n = int(empresa.presupuesto / empresa.salario)
        if n > 0:
            empresas_formales.append(empresa)
            vacantes_formales.append(n)

    for trabajador in estado.trabajadores:

        if trabajador.contrato is not None:

            contrato = trabajador.contrato

            if contrato.vence <= estado.día:
                trabajador.contrato = None

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

            trabajador.presupuesto += empresa.salario
            empresa.presupuesto -= empresa.salario

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

    if estado.config.salario_mínimo_automático and estado.config.salario_mínimo < salario_máximo * estado.config.tasa_salario_mínimo:
        estado.config.salario_mínimo = salario_máximo * estado.config.tasa_salario_mínimo

    trabajadores_sin_contrato = [
        trabajador
        for trabajador in estado.trabajadores
        if trabajador.contrato is None
    ]

    empresas_informales = []
    vacantes_informales = []

    if trabajadores_sin_contrato:

        for empresa in estado.empresas:
            n = int(min(estado.config.informalidad_por_empresa, empresa.presupuesto / empresa.salario_informal))
            if n > 0:
                empresas_informales.append(empresa)
                vacantes_informales.append(n)

        for trabajador in trabajadores_sin_contrato:

            if not empresas_informales:
                break

            i = estado.aleatorio.choices(
                range(len(empresas_informales)),
                weights=vacantes_informales,
                k=1
            )[0]

            empresa = empresas_informales[i]

            trabajador.contrato = Contrato(
                empresa=empresa,
                vence=estado.día + estado.config.duración_contrato,
                tipo="informal"
            )

            trabajador.presupuesto += empresa.salario_informal
            empresa.presupuesto -= empresa.salario_informal

            empresa.salario_informal *= (
                estado.config.reducción_salario_contratación
            )

            vacantes_informales[i] -= 1

            if vacantes_informales[i] == 0:
                vacantes_informales.pop(i)
                empresas_informales.pop(i)

    for empresa, vacantes in zip(empresas_formales, vacantes_formales):
        empresa.salario *= (
            estado.config.aumento_salario_vacante ** vacantes
        )

    for empresa, vacantes in zip(empresas_informales, vacantes_informales):
        empresa.salario_informal *= (
            estado.config.aumento_salario_vacante ** vacantes
        )