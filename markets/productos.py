# --- productos.py ---

def mercado_productos(estado):
    empresas_vendedoras = []
    productos_diarios = []

    for empresa in estado.empresas:
        if empresa.stock > 0:
            empresas_vendedoras.append(empresa)
            productos_diarios.append(empresa.stock)

    ventas_hoy = {empresa: 0 for empresa in estado.empresas}

    for trabajador in estado.trabajadores:
        if estado.aleatorio.random() <= estado.config.probabilidad_compra:
            if not empresas_vendedoras:
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
                empresa.precio *= estado.config.aumento_precio
                
                ventas_hoy[empresa] += 1
                empresa.stock -= 1
                
                productos_diarios[i] -= 1
                if productos_diarios[i] == 0:
                    productos_diarios.pop(i)
                    empresas_vendedoras.pop(i)
            else:
                empresa.precio *= estado.config.reducción_precio

    for empresa in estado.empresas:
        stock_inicial = empresa.stock + ventas_hoy[empresa]
        if stock_inicial > 0:
            stock_restante = stock_inicial - ventas_hoy[empresa]
            if stock_restante > 0:
                factor_reducción = (estado.config.reducción_precio) ** stock_restante
                empresa.precio *= factor_reducción