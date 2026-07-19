from collections import deque

def mercado_productos(estado):
    productos_disponibles = []

    for empresa in estado.empresas:
        empresa.producción = int(empresa.presupuesto / (empresa.precio * 0.4))
        empresa.inventario += empresa.producción
        empresa.unidades_vendidas = 0

        productos_disponibles.extend([empresa] * empresa.inventario)

    productos_disponibles.sort(key=lambda e: e.precio)
    productos_disponibles = deque(productos_disponibles)

    for trabajador in estado.trabajadores:
        if productos_disponibles:
            if trabajador.presupuesto >= productos_disponibles[0].precio:
                seleccionado = productos_disponibles.popleft()
                seleccionado.presupuesto += seleccionado.precio
                trabajador.presupuesto -= seleccionado.precio
                seleccionado.unidades_vendidas += 1
                seleccionado.inventario -= 1
        else:
            break

    for empresa in estado.empresas:
        if empresa.producción > empresa.unidades_vendidas:
            empresa.precio *= estado.config.reducción_precio
        elif empresa.producción < empresa.unidades_vendidas:
            empresa.precio *= estado.config.aumento_precio