def mercado_productos(estado):

    productos_disponibles = [empresa for empresa in estado.empresas for vacante in range(1)]
    productos_disponibles.sort(key=lambda e: e.precio)

    for trabajador in estado.trabajadores:
        if not productos_disponibles:
            break

        empresa = productos_disponibles.pop(0)

        if trabajador.presupuesto >= empresa.precio:
            trabajador.presupuesto -= empresa.precio
            empresa.presupuesto += empresa.precio
            empresa.precio *= estado.config.aumento_precio

            productos_disponibles[i] = productos_disponibles[-1]
            productos_disponibles.pop()

    for empresa in productos_disponibles:
        empresa.precio *= estado.config.reducción_precio