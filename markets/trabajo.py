def mercado_laboral(estado):

    vacantes = {
        empresa: int(empresa.presupuesto / empresa.salario)
        for empresa in estado.empresas
    }

    vacantes_totales = sum(vacantes.values())

    for trabajador in estado.trabajadores:
        if vacantes_totales == 0:
            break

        objetivo = estado.aleatorio.randrange(vacantes_totales)

        acumuladas = 0
        for empresa, cantidad in vacantes.items():
            acumuladas += cantidad
            if objetivo < acumuladas:
                break

        trabajador.presupuesto += empresa.salario
        empresa.presupuesto -= empresa.salario
        empresa.salario *= estado.config.reducción_salario

        vacantes[empresa] -= 1
        vacantes_totales -= 1

    for empresa, cantidad in vacantes.items():
        if cantidad:
            empresa.salario *= estado.config.aumento_salario