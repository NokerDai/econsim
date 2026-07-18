def mercado_productos(estado):
    for trabajador in estado.trabajadores:
        seleccionado = estado.aleatorio.choice(estado.empresas)
        if trabajador.presupuesto >= seleccionado.precio:
            seleccionado.presupuesto += seleccionado.precio
            trabajador.presupuesto -= seleccionado.precio
            seleccionado.precio *= estado.config.aumento_precio
        else:
            seleccionado.precio *= estado.config.reducción_precio