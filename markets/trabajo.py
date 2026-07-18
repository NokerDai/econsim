# --- trabajo.py ---

from models import Contrato


def mercado_laboral(estado):
    salario_máximo = 0

    empresas_formales = []
    vacantes_formales = []

    for trabajador in estado.trabajadores:
        if trabajador.contrato is not None:
            contrato = trabajador.contrato
            if contrato.vence <= estado.día:
                trabajador.contrato = None


    for empresa in estado.empresas:
        n = int(empresa.presupuesto / empresa.salario)
        if n > 0:
            empresas_formales.append(empresa)
            vacantes_formales.append(n)


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

    if estado.config.salario_mínimo_automático and estado.config.salario_mínimo < salario_máximo * estado.config.tasa_salario_mínimo:
        estado.config.salario_mínimo = salario_máximo * estado.config.tasa_salario_mínimo


    for empresa, vacantes in zip(empresas_formales, vacantes_formales):
        empresa.salario *= (
            estado.config.aumento_salario_vacante ** vacantes
        )