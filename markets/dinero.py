def emisión_monetaria(estado):

    emisión_por_trabajador = (
        estado.config.emisión_diaria /
        estado.config.num_trabajadores
    )

    for trabajador in estado.trabajadores:

        trabajador.presupuesto += emisión_por_trabajador