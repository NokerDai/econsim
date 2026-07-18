def emisión_monetaria(estado):

    tasa = estado.config.tasa_emisión

    for trabajador in estado.trabajadores:

        trabajador.presupuesto *= 1 + tasa