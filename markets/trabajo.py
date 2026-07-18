def mercado_laboral(estado):

    vacantes_formales = [empresa for empresa in estado.empresas for vacante in range(int(empresa.presupuesto / empresa.salario))]
    estado.aleatorio.shuffle(vacantes_formales)

    for trabajador in estado.trabajadores:
        if not vacantes_formales:
            break

        empresa = estado.aleatorio.pop(0)

        trabajador.presupuesto += empresa.salario
        empresa.presupuesto -= empresa.salario
        empresa.salario *= estado.config.reducción_salario

    for empresa in estado.empresas:
        empresa.salario *= estado.config.aumento_salario