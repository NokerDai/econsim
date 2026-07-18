def mercado_laboral(estado):
    vacantes_diarias = [empresa
                  for empresa in estado.empresas
                  for vacante in range(int(empresa.presupuesto / empresa.salario))]
    vacantes_diarias.sort(key=lambda e: e.salario, reverse=True)

    for trabajador in estado.trabajadores:
        trabajador.trabajo = False
        if vacantes_diarias:
            trabajador.trabajo = True
            seleccionada = vacantes_diarias[0]
            if estado.config.salario_mínimo_automático and seleccionada.salario > estado.config.salario_mínimo * estado.config.tasa_salario_mínimo:
                estado.config.salario_mínimo = seleccionada.salario
            trabajador.presupuesto += seleccionada.salario
            seleccionada.presupuesto -= seleccionada.salario
            seleccionada.salario = max(seleccionada.salario * estado.config.reducción_salario, estado.config.salario_mínimo)
            vacantes_diarias.remove(seleccionada)

    for vacante in vacantes_diarias:
        vacante.salario *= estado.config.aumento_salario

    trabajadores_desempleados = [trabajador for trabajador in estado.trabajadores if not trabajador.trabajo]
    if trabajadores_desempleados:
        vacantes_diarias = [empresa
                  for empresa in estado.empresas
                  for vacante in range(int(empresa.presupuesto / empresa.salario_informal))]
        vacantes_diarias.sort(key=lambda e: e.salario_informal, reverse=True)

        for trabajador in trabajadores_desempleados:
            if not vacantes_diarias:
                break
            else:
                trabajador.trabajo = True
                seleccionada = vacantes_diarias[0]
                trabajador.presupuesto += seleccionada.salario_informal
                seleccionada.presupuesto -= seleccionada.salario_informal
                seleccionada.salario_informal *= estado.config.reducción_salario
                vacantes_diarias.remove(seleccionada)

        for vacante in vacantes_diarias:
            vacante.salario_informal *= estado.config.aumento_salario