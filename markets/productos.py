def mercado_productos(estado):

    for trabajador in estado.trabajadores:

        empresa = estado.aleatorio.choice(estado.empresas)

        if trabajador.presupuesto >= empresa.precio:

            trabajador.presupuesto -= empresa.precio

            empresa.presupuesto += empresa.precio

            empresa.ventas_mes += 1

    if estado.día % estado.config.período_actualización_precios == 0:

        for empresa in estado.empresas:

            if empresa.ventas_mes < empresa.ventas_mes_anterior:

                empresa.precio *= estado.config.reducción_precio

            elif empresa.ventas_mes > empresa.ventas_mes_anterior:

                empresa.precio *= estado.config.aumento_precio

            empresa.ventas_mes_anterior = empresa.ventas_mes
            empresa.ventas_mes = 0