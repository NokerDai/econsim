def mercado_laboral(estado):

    vacantes_formales = [empresa for empresa in estado.empresas for vacante in range(int(empresa.presupuesto / empresa.salario))]

    for trabajador in estado.trabajadores:
        if not vacantes_formales:
            break

        i = estado.aleatorio.randrange(len(vacantes_formales))
        empresa = vacantes_formales[i]

        trabajador.presupuesto += empresa.salario
        empresa.presupuesto -= empresa.salario
        empresa.salario *= estado.config.reducción_salario

        vacantes_formales[i] = vacantes_formales[-1]
        vacantes_formales.pop()

    for empresa in vacantes_formales:
        empresa.salario *= estado.config.aumento_salario