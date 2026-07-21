from ui.fenwick import FenwickTree


def mercado_productos(estado):
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    # Producción
    for empresa in estado.empresas:
        empresa.ventas_hoy = 0
        empresa.inventario += (
            (empresa.empleados_formales * pf +
             empresa.empleados_informales * pi)
            * empresa.productividad
        )

    empresas = estado.empresas

    # Árbol de Fenwick con el stock disponible
    fenwick = FenwickTree([
        int(empresa.inventario)
        for empresa in empresas
    ])

    indice_empresa = {
        empresa: i
        for i, empresa in enumerate(empresas)
    }

    sp = estado.config.sensibilidad_precio
    sc = estado.config.sensibilidad_calidad

    for trabajador in estado.trabajadores:

        if fenwick.total == 0:
            break

        peso_precio = trabajador.sensibilidad_precio * sp
        peso_calidad = trabajador.sensibilidad_calidad * sc

        opciones = []
        extraidas = []

        cantidad = min(10, fenwick.total)

        # Extraer 10 productos SIN reemplazo
        for _ in range(cantidad):

            r = estado.aleatorio.randint(1, fenwick.total)

            idx = fenwick.find(r)

            opciones.append(empresas[idx])
            extraidas.append(idx)

            # Sacar temporalmente una unidad
            fenwick.add(idx, -1)

        seleccionado = max(
            opciones,
            key=lambda e:
                e.calidad * peso_calidad
                - e.precio * peso_precio
        )

        compro = trabajador.presupuesto >= seleccionado.precio

        if compro:
            seleccionado.presupuesto += seleccionado.precio
            trabajador.presupuesto -= seleccionado.precio

            seleccionado.inventario -= 1
            seleccionado.ventas_hoy += 1

            idx_seleccionado = indice_empresa[seleccionado]
        else:
            idx_seleccionado = None

        # Restaurar todas las unidades excepto la comprada
        restaurado = False

        for idx in extraidas:
            if compro and idx == idx_seleccionado and not restaurado:
                restaurado = True
                continue
            fenwick.add(idx, 1)

    # Ajuste de precios y productividad
    for empresa in empresas:

        empresa.precio_venta_real = empresa.precio

        if empresa.inventario > empresa.inventario_ayer:
            empresa.racha_reducido += 1
            empresa.racha_aumentado = 0
            empresa.precio *= estado.config.reducción_precio

        elif empresa.inventario < empresa.inventario_ayer:
            empresa.racha_aumentado += 1
            empresa.racha_reducido = 0
            empresa.precio *= estado.config.aumento_precio

        if empresa.racha_reducido > 30:
            empresa.productividad *= 0.99

        elif empresa.racha_aumentado > 30:
            empresa.productividad *= 1.01

        empresa.inventario_ayer = empresa.inventario