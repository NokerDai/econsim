# --- productos.py ---
from itertools import islice

def mercado_productos(estado):
    productos_disponibles = []
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    for empresa in estado.empresas:
        empresa.ventas_hoy = 0
        empresa.inventario += (empresa.empleados_formales * pf + empresa.empleados_informales * pi) * empresa.productividad
        productos_disponibles.extend([empresa] * int(min(estado.config.num_trabajadores, empresa.inventario)))

    estado.aleatorio.shuffle(productos_disponibles)

    sp = estado.config.sensibilidad_precio
    sc = estado.config.sensibilidad_calidad

    for trabajador in estado.trabajadores:
        if productos_disponibles:
            opciones_trabajador = list(islice(productos_disponibles, 10))
            opciones_trabajador.sort(key=lambda e: e.calidad * trabajador.sensibilidad_calidad * sc - e.precio * trabajador.sensibilidad_precio * sp, reverse=True)
            seleccionado = opciones_trabajador[0]

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