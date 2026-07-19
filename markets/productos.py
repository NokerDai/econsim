from collections import deque

def mercado_productos(estado):
    productos_disponibles = []
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    for empresa in estado.empresas:
        empresa.inventario += (empresa.empleados_formales * pf + empresa.empleados_informales * pi) * empresa.productividad
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
            empresa.racha_reducido += 1
            empresa.racha_aumentado = 0
            empresa.precio *= estado.config.reducción_precio
        elif empresa.inventario < empresa.inventario_ayer:
            empresa.racha_aumentado += 1
            empresa.racha_reducido = 0
            empresa.precio *= estado.config.aumento_precio
        if empresa.racha_reducido > 30:
            empresa.productividad *= 0.99
        elif empresa.racha_aumentado > 30:
            empresa.productividad *= 1.01
        empresa.inventario_ayer = empresa.inventario