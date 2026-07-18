def mercado_productos(estado):
    # Identificar empresas que tienen stock para vender hoy
    empresas_vendedoras = []
    productos_diarios = []

    for empresa in estado.empresas:
        if empresa.stock > 0:
            empresas_vendedoras.append(empresa)
            productos_diarios.append(empresa.stock)

    stock_inicial_hoy = {empresa: empresa.stock for empresa in estado.empresas}
    ventas_hoy = {empresa: 0 for empresa in estado.empresas}

    for trabajador in estado.trabajadores:
        if estado.aleatorio.random() <= estado.config.probabilidad_compra:
            if not empresas_vendedoras:
                for emp in estado.empresas:
                    emp.precio *= estado.config.aumento_precio
                break

            i = estado.aleatorio.choices(
                range(len(empresas_vendedoras)),
                weights=productos_diarios,
                k=1
            )[0]

            empresa = empresas_vendedoras[i]

            if trabajador.presupuesto >= empresa.precio:
                trabajador.presupuesto -= empresa.precio
                empresa.presupuesto += empresa.precio
                
                empresa.precio *= estado.config.reducción_precio
                
                ventas_hoy[empresa] += 1
                empresa.stock -= 1
                
                productos_diarios[i] -= 1
                if productos_diarios[i] == 0:
                    productos_diarios.pop(i)
                    empresas_vendedoras.pop(i)


    for empresa in estado.empresas:
        stock_sobrante = empresa.stock

        if stock_sobrante > 0:
            empresa.precio *= (estado.config.reducción_precio ** stock_sobrante)
        else:
            if stock_inicial_hoy[empresa] > 0:
                empresa.precio *= estado.config.aumento_precio