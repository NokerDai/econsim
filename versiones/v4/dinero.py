def emisión_monetaria(estado):
    config = estado.config

    tasa = 1
    if estado.config.tasa_emisión != 0:
        tasa = 1 + estado.config.tasa_emisión
    else:
        num_empresas = estado.config.num_empresas
        num_trabajadores = estado.config.num_trabajadores
        M0_inicial = estado.config.presupuesto_inicial * num_empresas
        M0_actual = sum(t.presupuesto for t in estado.trabajadores) + sum(e.presupuesto for e in estado.empresas)

        if config.mantenimiento_M0 == "agentes" or config.mantenimiento_M0 == "mixto":
            peso_trabajadores = num_empresas / num_trabajadores

            M0_pt_inicial = M0_inicial / num_trabajadores
            M0_pe_inicial = estado.config.presupuesto_inicial

            M0_pt_actual = M0_actual / len(estado.trabajadores)
            M0_pe_actual = M0_actual / len(estado.empresas)

            objetivo = (
                peso_trabajadores * M0_pt_inicial +
                (1 - peso_trabajadores) * M0_pe_inicial
            )

            actual = (
                peso_trabajadores * M0_pt_actual +
                (1 - peso_trabajadores) * M0_pe_actual
            )

            tasa = max(tasa, (objetivo / actual + estado.config.mantenimiento_M0_suavizado) / (estado.config.mantenimiento_M0_suavizado + 1))

        if config.mantenimiento_M0 == "ventas" or config.mantenimiento_M0 == "mixto":
            ventas = estado.estadisticas.bienes_vendidos[-1]
            ventas_ref = estado.ventas_referencia
            M0_pv_ref = M0_inicial / ventas_ref

            objetivo = M0_pv_ref * ventas
            tasa = max(tasa, (objetivo / M0_actual + estado.config.mantenimiento_M0_suavizado) / (estado.config.mantenimiento_M0_suavizado + 1))


    for trabajador in estado.trabajadores:

        trabajador.presupuesto *= tasa

    for empresa in estado.empresas:

        empresa.presupuesto *= tasa