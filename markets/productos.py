# --- productos.py ---

def mercado_productos(estado):
    for empresa in estado.empresas:
        empresa.inventario = (empresa.empleados_formales * estado.config.productividad_formal) + (empresa.empleados_informales * estado.config.productividad_informal)

    for trabajador in estado.trabajadores:
        seleccionado = estado.aleatorio.choice(estado.empresas)
        
        if trabajador.presupuesto >= seleccionado.precio and seleccionado.inventario >= 1:
            seleccionado.presupuesto += seleccionado.precio
            trabajador.presupuesto -= seleccionado.precio
            seleccionado.inventario -= 1
            
            seleccionado.precio *= estado.config.aumento_precio
        elif seleccionado.inventario >= 1:
            seleccionado.precio *= estado.config.reducción_precio