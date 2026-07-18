def mercado_laboral(estado):

    vacantes = [
        [empresa, int(empresa.presupuesto / empresa.salario)]
        for empresa in estado.empresas
    ]

    vacantes_totales = sum(c for _, c in vacantes)

    for trabajador in estado.trabajadores:
        if vacantes_totales == 0:
            break

        objetivo = estado.aleatorio.randrange(vacantes_totales)

        acumuladas = 0
        for i, (empresa, cantidad) in enumerate(vacantes):
            acumuladas += cantidad
            if objetivo < acumuladas:
                break

        trabajador.presupuesto += empresa.salario
        empresa.presupuesto -= empresa.salario
        empresa.salario *= estado.config.reducción_salario

        vacantes[i][1] -= 1
        vacantes_totales -= 1

    for empresa, cantidad in vacantes:
        if cantidad > 0:
            empresa.salario *= estado.config.aumento_salario