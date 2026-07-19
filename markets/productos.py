# --- productos.py ---

def mercado_productos(estado):
    for empresa in estado.empresas:
        empresa.inventario += 10

    for trabajador in estado.trabajadores:
        seleccionado = estado.aleatorio.choice(estado.empresas)
        
        if trabajador.presupuesto >= seleccionado.precio and seleccionado.inventario >= 1:
            seleccionado.presupuesto += seleccionado.precio
            trabajador.presupuesto -= seleccionado.precio
            empresa.unidades_vendidas += 1
            seleccionado.inventario -= 1

    for empresa in estado.empresas:
        empresa.precio *= estado.config.reducción_precio ** empresa.inventario * estado.config.aumento_precio ** empresa.unidades_vendidas
        empresa.unidades_vendidas = 0