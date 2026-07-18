def mercado_productos(estado):

    empresas = estado.empresas
    aleatorio = estado.aleatorio
    aumento = estado.config.aumento_precio
    reduccion = estado.config.reducción_precio

    for trabajador in estado.trabajadores:

        empresa = aleatorio.choice(empresas)

        if trabajador.presupuesto >= empresa.precio:
            precio = empresa.precio

            trabajador.presupuesto -= precio
            empresa.presupuesto += precio
            empresa.precio = precio * aumento

        else:
            empresa.precio *= reduccion