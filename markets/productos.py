def mercado_productos(estado):

    for trabajador in estado.trabajadores:

        empresa = estado.aleatorio.choice(estado.empresas)

        if trabajador.presupuesto >= empresa.precio:

            trabajador.presupuesto -= empresa.precio

            empresa.presupuesto += empresa.precio

            empresa.precio *= estado.config.aumento_precio

        else:
            
            empresa.precio *= estado.config.reducción_precio