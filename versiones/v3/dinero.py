def emisión_monetaria(estado):

    tasa = 1
    if estado.config.mantenimiento_M0 and estado.config.tasa_emisión == 0:
        num_empresas = estado.config.num_empresas
        num_trabajadores = estado.config.num_trabajadores

        M0_inicial = estado.config.presupuesto_inicial * num_empresas
        M0_pt_inicial = M0_inicial / num_trabajadores
        M0_pe_inicial = estado.config.presupuesto_inicial
        i = M0_pt_inicial + M0_pe_inicial

        M0_actual = sum(t.presupuesto for t in estado.trabajadores) + sum(e.presupuesto for e in estado.empresas)
        M0_pt_actual = M0_actual / len(estado.trabajadores)
        M0_pe_actual = M0_actual / len(estado.empresas)
        a = M0_pt_actual + M0_pe_actual

        tasa = max(1, (i / a + estado.config.mantenimiento_M0_suavizado) / (estado.config.mantenimiento_M0_suavizado + 1))
    else:
        tasa = 1 + estado.config.tasa_emisión

    for trabajador in estado.trabajadores:

        trabajador.presupuesto *= tasa

    for empresa in estado.empresas:

        empresa.presupuesto *= tasa