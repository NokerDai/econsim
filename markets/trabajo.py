def mercado_laboral(estado):

    vacantes_formales = [empresa for empresa in estado.empresas for vacante in range(int(empresa.presupuesto / empresa.salario))]
    vacantes_formales.sort(key=lambda e: e.salario, reverse=True)

    for trabajador in estado.trabajadores:
        if not vacantes_formales:
            break

        empresa = vacantes_formales.pop(0)

        trabajador.presupuesto += empresa.salario
        empresa.presupuesto -= empresa.salario
        empresa.salario *= estado.config.reducción_salario
        empresa.contrató = True

    for empresa in estado.empresas:
        if not empresa.contrató:
            empresa.salario *= estado.config.aumento_salario
        empresa.contrató = False