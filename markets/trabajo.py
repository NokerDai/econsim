def mercado_laboral(estado):

    vacantes_formales = [empresa for empresa in estado.empresas for vacante in range(int(empresa.presupuesto / empresa.salario))]

    for trabajador in estado.trabajadores:

        empresa = estado.aleatorio.choice(vacantes_formales)

        trabajador.presupuesto += empresa.salario

        empresa.presupuesto -= empresa.salario

        empresa.salario *= estado.config.reducción_salario

        vacantes_formales.remove(empresa)

    for empresa in vacantes_formales:
        
        empresa.salario *= estado.config.aumento_salario