# --- productos.py ---

def mercado_productos(estado):
    for trabajador in estado.trabajadores:
        empresa = estado.aleatorio.choice(estado.empresas)
        if trabajador.presupuesto >= empresa.precio:
            trabajador.presupuesto -= empresa.precio
            empresa.presupuesto += empresa.precio
            empresa.ventas += 1

    if estado.día % estado.config.intervalo_ajuste == 0:
        for empresa in estado.empresas:
            if empresa.ventas < empresa.ventas_anteriores:
                empresa.precio *= estado.config.reducción_precio ** (empresa.ventas_anteriores - empresa.ventas)
            elif empresa.ventas > empresa.ventas_anteriores:
                empresa.precio *= estado.config.aumento_precio ** (empresa.ventas - empresa.ventas_anteriores)
            empresa.ventas_anteriores = empresa.ventas
            empresa.ventas = 0