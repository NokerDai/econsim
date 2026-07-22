# --- productos.py ---

def mercado_productos(estado):
    productos_disponibles = []
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    for empresa in estado.empresas:
        empresa.ventas_hoy = 0
        empresa.días_sin_vender += 1
        produccion_formal = empresa.productividad_acumulada_formales * pf
        produccion_informal = empresa.productividad_acumulada_informales * pi
        empresa.inventario += (produccion_formal + produccion_informal) * empresa.productividad
        productos_disponibles.extend([empresa] * int(min(len(estado.trabajadores), empresa.inventario)))

    sp = estado.config.sensibilidad_precio
    sc = estado.config.sensibilidad_calidad
    rand = estado.aleatorio
    random_func = rand.random  # Acceso directo al generador en C, mucho más rápido

    for trabajador in estado.trabajadores:
        trabajador.días_sin_comprar += 1
        n_disp = len(productos_disponibles)
        if n_disp > 0:
            peso_calidad = trabajador.sensibilidad_calidad * sc
            peso_precio = trabajador.sensibilidad_precio * sp

            k = min(10, n_disp)
            
            # 1. Muestreo de k índices únicos ultra rápido (Rejection Sampling)
            # Como k es máximo 10, la probabilidad de colisión es despreciable
            indices = []
            if k == n_disp:
                indices = list(range(n_disp))
            else:
                seen = set()
                for _ in range(k):
                    idx = int(random_func() * n_disp)
                    while idx in seen:
                        idx = int(random_func() * n_disp)
                    seen.add(idx)
                    indices.append(idx)
            
            # 2. Búsqueda del mejor producto sin el coste de funciones lambda o sort
            best_idx_in_list = -1
            best_score = -float('inf')
            seleccionado = None
            
            for idx in indices:
                emp = productos_disponibles[idx]
                score = emp.calidad * peso_calidad - emp.precio * peso_precio
                if score > best_score:
                    best_score = score
                    best_idx_in_list = idx
                    seleccionado = emp

            # 3. Transacción si el presupuesto lo permite
            if trabajador.presupuesto >= seleccionado.precio:
                seleccionado.presupuesto += seleccionado.precio
                trabajador.presupuesto -= seleccionado.precio
                seleccionado.inventario -= 1
                seleccionado.ventas_hoy += 1
                trabajador.días_sin_comprar = 0
                seleccionado.días_sin_vender = 0
                
                # 4. Eliminación O(1) con swap-and-pop
                # Intercambiamos el elemento comprado por el último de la lista y hacemos pop()
                last_idx = len(productos_disponibles) - 1
                if best_idx_in_list != last_idx:
                    productos_disponibles[best_idx_in_list] = productos_disponibles[last_idx]
                productos_disponibles.pop()
        else:
            break

    # Ajustes de precio y productividad de las empresas
    for empresa in estado.empresas:
        empresa.precio_venta_real = empresa.precio
        if empresa.inventario > empresa.inventario_ayer:
            empresa.racha_reducido += 1
            empresa.racha_aumentado = 0
            empresa.precio *= estado.config.reducción_precio
        elif empresa.inventario < empresa.inventario_ayer:
            empresa.racha_aumentado += 1
            empresa.racha_reducido = 0
            empresa.precio *= estado.config.aumento_precio
        else:
            empresa.racha_reducido = 0
            empresa.racha_aumentado = 0
            
        if empresa.racha_reducido > 30:
            empresa.productividad *= 0.99
        elif empresa.racha_aumentado > 30:
            empresa.productividad *= 1.01
            
        empresa.inventario_ayer = empresa.inventario