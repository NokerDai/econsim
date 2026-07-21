from collections import deque

def mercado_productos(estado):
    productos_disponibles = []
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    for empresa in estado.empresas:
        empresa.ventas_hoy = 0
        empresa.inventario += (empresa.empleados_formales * pf + empresa.empleados_informales * pi) * empresa.productividad
        productos_disponibles.extend([empresa] * int(empresa.inventario))

    productos_disponibles = deque(productos_disponibles)

    for trabajador in estado.trabajadores:
        if productos_disponibles:
            candidatos = estado.aleatorio.sample(list(productos_disponibles), min(20, len(productos_disponibles)))
            seleccionado = max(
                candidatos,
                key=lambda empresa:
                    trabajador.sensibilidad_calidad * empresa.calidad
                    - trabajador.sensibilidad_precio * empresa.precio
            )
            if trabajador.presupuesto >= seleccionado.precio:
                seleccionado.presupuesto += seleccionado.precio
                trabajador.presupuesto -= seleccionado.precio
                seleccionado.inventario -= 1
                seleccionado.ventas_hoy += 1
                productos_disponibles.remove(seleccionado)
        else:
            break

    for empresa in estado.empresas:
        empresa.precio_venta_real = empresa.precio
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