def mercado_laboral(estado):
    vacantes_diarias = [empresa
                  for empresa in estado.empresas
                  for vacante in range(int((empresa.presupuesto) / empresa.salario))]
    vacantes_diarias.sort(key=lambda e: e.salario, reverse=True)

    for trabajador in estado.trabajadores:
        if vacantes_diarias:
            seleccionada = vacantes_diarias[0]
            trabajador.presupuesto += seleccionada.salario
            seleccionada.presupuesto -= seleccionada.salario
            seleccionada.salario *= estado.config.reducción_salario
            vacantes_diarias.remove(seleccionada)

    for vacante in vacantes_diarias:
        vacante.salario *= estado.config.aumento_salario