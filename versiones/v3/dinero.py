def emisión_monetaria(estado):

    tasa = 1
    if estado.config.mantenimiento_M0 and estado.config.tasa_emisión == 0:
        M0_pc_inicial = estado.config.presupuesto_inicial * estado.config.num_empresas
        M0_pc_actual = sum([e.presupuesto for e in estado.empresas]) + sum([t.presupuesto for t in estado.trabajadores])
        if M0_pc_actual < M0_pc_inicial:
            tasa = (M0_pc_inicial / M0_pc_actual + estado.config.mantenimiento_M0_suavizado) / (estado.config.mantenimiento_M0_suavizado + 1)
    else:
        tasa = 1 + estado.config.tasa_emisión

    for trabajador in estado.trabajadores:

        trabajador.presupuesto *= tasa

    for empresa in estado.empresas:

        empresa.presupuesto *= tasa