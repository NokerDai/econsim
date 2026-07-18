def mercado_laboral(estado):
    vacantes_formales = []
    for empresa in estado.empresas:
        empresa.vacantes_formales = int(empresa.presupuesto / empresa.salario)
        empresa.vacantes_informales = 0
        empresa.empleados_formales = 0
        empresa.empleados_informales = 0
        vacantes_formales.extend([empresa] * empresa.vacantes_formales)
    vacantes_formales.sort(key=lambda e: e.salario, reverse=True)
    
    informalidad = False
    vacantes_informales = []

    for trabajador in estado.trabajadores:
        if vacantes_formales:
            seleccionada = vacantes_formales[0]
            seleccionada.empleados_formales += 1
            if estado.config.salario_mínimo_automático and seleccionada.salario > estado.config.salario_mínimo:
                estado.config.salario_mínimo = seleccionada.salario * estado.config.tasa_salario_mínimo
            trabajador.salario = seleccionada.salario
            trabajador.presupuesto += seleccionada.salario
            seleccionada.presupuesto -= seleccionada.salario
            vacantes_formales.remove(seleccionada)
        elif informalidad:
            if not vacantes_informales:
                break
            else:
                seleccionada = vacantes_informales[0]
                seleccionada.empleados_informales += 1
                trabajador.salario = seleccionada.salario_informal
                trabajador.presupuesto += seleccionada.salario_informal
                seleccionada.presupuesto -= seleccionada.salario_informal
                vacantes_informales.remove(seleccionada)
        else:
            informalidad = True
            for empresa in estado.empresas:
                empresa.vacantes_informales = int(min(estado.config.informalidad_por_empresa, empresa.presupuesto / empresa.salario_informal))
                vacantes_informales.extend([empresa] * empresa.vacantes_informales)
            vacantes_informales.sort(key=lambda e: e.salario, reverse=True)

    for empresa in estado.empresas:
        seleccionada.salario = max(seleccionada.salario * estado.config.reducción_salario ** empresa.empleados_formales, estado.config.salario_mínimo)
        seleccionada.salario *= estado.config.aumento_salario ** (empresa.vacantes_formales - empresa.empleados_formales)
        seleccionada.salario_informal *= estado.config.reducción_salario ** empresa.empleados_informales
        seleccionada.salario_informal *= estado.config.aumento_salario ** (empresa.vacantes_informales - empresa.empleados_informales)