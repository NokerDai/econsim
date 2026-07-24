# --- productos.py ---
import math

def mercado_productos(estado):
    productos_disponibles = []
    pf = estado.config.productividad_formal
    pi = estado.config.productividad_informal

    # 1. Fase de Producción y actualización de inventario
    for empresa in estado.empresas:
        empresa.ventas_hoy = 0
        empresa.días_sin_vender += 1
        produccion_formal = empresa.productividad_acumulada_formales * pf
        produccion_informal = empresa.productividad_acumulada_informales * pi
        producción = (produccion_formal + produccion_informal) * empresa.productividad
        empresa.producción = producción
        empresa.inventario += producción

    sp = estado.config.sensibilidad_precio
    sc = estado.config.sensibilidad_calidad
    rand = estado.aleatorio
    random_func = rand.random  # Acceso directo al generador rápido

    # 2. Mercado de Consumo (Modelo de Elección Discreta con Opción de Reserva)
    for trabajador in estado.trabajadores:
        trabajador.días_sin_comprar += 1
        
        # Filtrar empresas que tienen stock y cuyo precio es estrictamente menor al presupuesto
        active_firms = [
            emp for emp in estado.empresas 
            if emp.inventario >= 1.0 and trabajador.presupuesto > emp.precio
        ]
        
        n_disp = len(active_firms)
        if n_disp > 0:
            # Determinación de un conjunto de consideración acotado (Búsqueda aleatoria de hasta k opciones)
            k = min(10, n_disp)
            sampled_firms = []
            if k == n_disp:
                sampled_firms = active_firms
            else:
                seen_indices = set()
                while len(sampled_firms) < k:
                    idx = int(random_func() * n_disp)
                    if idx not in seen_indices:
                        seen_indices.add(idx)
                        sampled_firms.append(active_firms[idx])
            
            peso_calidad = trabajador.sensibilidad_calidad * sc
            peso_precio = trabajador.sensibilidad_precio * sp
            
            # Evaluación de la opción de reserva (No comprar, conservar todo el dinero)
            # Utlizamos Gumbel(0,1) mediante el método de transformación inversa
            u_noise = random_func()
            u_noise = max(1e-15, min(u_noise, 1.0 - 1e-15))
            eps_0 = -math.log(-math.log(u_noise))
            
            # Utilidad del dinero ahorrado
            v_0 = peso_precio * math.log(max(trabajador.presupuesto, 1e-5))
            best_utility = v_0 + eps_0
            seleccionado = None  # Representa la opción externa
            
            # Evaluación de las alternativas de mercado
            for emp in sampled_firms:
                u_noise = random_func()
                u_noise = max(1e-15, min(u_noise, 1.0 - 1e-15))
                eps_j = -math.log(-math.log(u_noise))
                
                # Utilidad: peso_calidad * calidad + peso_precio * ln(presupuesto - precio)
                v_j = peso_calidad * emp.calidad + peso_precio * math.log(trabajador.presupuesto - emp.precio)
                u_j = v_j + eps_j
                
                if u_j > best_utility:
                    best_utility = u_j
                    seleccionado = emp
            
            # Si el consumidor prefiere un bien del mercado a la opción de reserva
            if seleccionado is not None and seleccionado.inventario >= 1.0:
                seleccionado.presupuesto += seleccionado.precio
                trabajador.presupuesto -= seleccionado.precio
                seleccionado.inventario -= 1
                seleccionado.ventas_hoy += 1
                trabajador.días_sin_comprar = 0
                seleccionado.días_sin_vender = 0

    # 3. Ajustes de Precio (Regla de Lerner con aprendizaje de elasticidad) y Productividad
    alpha = 0.1   # Tasa de aprendizaje de la probabilidad de venta
    phi = 0.15    # Velocidad de ajuste de precios (fricciones/costos de menú)
    delta = 0.05  # Tasa de actualización de la elasticidad estimada

    for empresa in estado.empresas:
        
        # Dinámica de productividad adaptativa basada en acumulación de inventario
        if empresa.inventario > empresa.inventario_ayer:
            empresa.racha_reducido += 1
            empresa.racha_aumentado = 0
        elif empresa.inventario < empresa.inventario_ayer:
            empresa.racha_aumentado += 1
            empresa.racha_reducido = 0
        else:
            empresa.racha_reducido = 0
            empresa.racha_aumentado = 0
            
        if empresa.racha_reducido > 30:
            empresa.productividad *= 0.99
        elif empresa.racha_aumentado > 30:
            empresa.productividad *= 1.01

        # Estimación del Costo Marginal (MC = Salarios Esperados / Producción Esperada)
        prod_esp = max(empresa.producción_esperada, 0.01)
        sal_esp = max(empresa.salarios_esperados, 1.0)
        costo_marginal = max(sal_esp / prod_esp, 1.0)

        # Aprendizaje bayesiano/recursivo de la elasticidad estimada de la demanda
        if not hasattr(empresa, 'elasticidad_estimada'):
            empresa.elasticidad_estimada = 2.0  # Valor inicial de elasticidad

        if empresa.inventario > empresa.inventario_ayer:
            # Exceso de inventario: la demanda es más elástica de lo previsto. 
            # Aumentamos la elasticidad estimada para reducir el margen de ganancia.
            empresa.elasticidad_estimada *= (1.0 + delta)
        elif empresa.inventario < empresa.inventario_ayer:
            # Escasez o vaciado de stock: la demanda es más inelástica de lo previsto.
            empresa.elasticidad_estimada *= (1.0 - delta)

        # Restricción de límites lógicos para evitar divisiones por cero o márgenes infinitos
        empresa.elasticidad_estimada = max(1.15, min(empresa.elasticidad_estimada, 10.0))

        # Regla de Lerner: P = MC * (epsilon / (epsilon - 1))
        markup = empresa.elasticidad_estimada / (empresa.elasticidad_estimada - 1.0)
        precio_objetivo = costo_marginal * markup

        # Suavizado de la transición del precio
        empresa.precio_venta_real = empresa.precio
        empresa.precio = (1.0 - phi) * empresa.precio + phi * precio_objetivo
        empresa.precio = max(empresa.precio, 1.0)
        
        # Guardar estado del inventario para el siguiente periodo
        empresa.inventario_ayer = empresa.inventario

        # ==========================
        # Actualización de Expectativas de la Empresa
        # ==========================

        empresa.producción_esperada = (
            (
                empresa.productividad_acumulada_formales * pf +
                empresa.productividad_acumulada_informales * pi
            )
            * empresa.productividad
        )

        if empresa.producción_esperada > 0:
            probabilidad_real = min(
                empresa.ventas_hoy / max(empresa.producción, 1.0),
                1.0
            )
            empresa.probabilidad_venta_esperada = (
                (1 - alpha) * empresa.probabilidad_venta_esperada +
                alpha * probabilidad_real
            )

        empresa.ingresos_esperados = (
            empresa.precio *
            empresa.producción_esperada *
            empresa.probabilidad_venta_esperada
        )

        empresa.salarios_esperados = (
            empresa.empleados_formales * empresa.salario +
            empresa.empleados_informales * empresa.salario_informal
        )

        empresa.otros_costos_esperados = 0.0

        empresa.beneficio_esperado = (
            empresa.ingresos_esperados
            - empresa.salarios_esperados
            - empresa.otros_costos_esperados
        )