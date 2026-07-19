# --- productos.py ---

def mercado_productos(estado):
    for empresa in estado.empresas:
        empresa.producción = int(empresa.presupuesto / (empresa.precio * 0.3))
        empresa.inventario += empresa.producción
        empresa.unidades_vendidas = 0

    for trabajador in estado.trabajadores:
        seleccionado = estado.aleatorio.choice(estado.empresas)
        
        if trabajador.presupuesto >= seleccionado.precio and seleccionado.inventario >= 1:
            seleccionado.presupuesto += seleccionado.precio
            trabajador.presupuesto -= seleccionado.precio
            seleccionado.unidades_vendidas += 1
            seleccionado.inventario -= 1

    for empresa in estado.empresas:
        if empresa.producción > empresa.unidades_vendidas:
            empresa.precio *= estado.config.reducción_precio
        elif empresa.producción < empresa.unidades_vendidas:
            empresa.precio *= estado.config.aumento_precio