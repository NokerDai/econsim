def mercado_productos(estado):

    productos_disponibles = [empresa for empresa in estado.empresas for vacante in range(1)]

    for trabajador in estado.trabajadores:
        if not productos_disponibles:
            break

        i = estado.aleatorio.randrange(len(productos_disponibles))
        empresa = productos_disponibles[i]

        trabajador.presupuesto -= empresa.precio
        empresa.presupuesto += empresa.precio
        empresa.precio *= estado.config.aumento_precio

        productos_disponibles[i] = productos_disponibles[-1]
        productos_disponibles.pop()

    for empresa in productos_disponibles:
        empresa.precio *= estado.config.reducción_precio