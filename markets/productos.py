from collections import deque

def mercado_productos(estado):
    productos_disponibles = []

    for empresa in estado.empresas:
        empresa.producción = empresa.presupuesto / (empresa.precio * 0.5)
        empresa.inventario += empresa.producción

        productos_disponibles.extend([empresa] * int(empresa.inventario))

    productos_disponibles.sort(key=lambda e: e.precio)
    productos_disponibles = deque(productos_disponibles)

    for trabajador in estado.trabajadores:
        if productos_disponibles:
            if trabajador.presupuesto >= productos_disponibles[0].precio:
                seleccionado = productos_disponibles.popleft()
                seleccionado.presupuesto += seleccionado.precio
                trabajador.presupuesto -= seleccionado.precio
                seleccionado.inventario -= 1
        else:
            break

    for empresa in estado.empresas:
        if empresa.inventario > empresa.inventario_ayer:
            empresa.precio *= estado.config.reducción_precio
        elif empresa.inventario < empresa.inventario_ayer:
            empresa.precio *= estado.config.aumento_precio
        empresa.inventario_ayer = empresa.inventario