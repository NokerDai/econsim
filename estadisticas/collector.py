# --- collector.py ---
def actualizar_estadisticas(estado):
    total_empresas = len(estado.empresas)
    total_trabajadores = len(estado.trabajadores)
    
    precio_lista_medio = sum(e.precio for e in estado.empresas) / total_empresas if total_empresas > 0 else 0.0

    total_ventas = sum(e.ventas_hoy for e in estado.empresas)

    # Corrección del promedio ponderado de calidad según las ventas
    if total_ventas > 0:
        calidad_media_transacción = sum(e.calidad * e.ventas_hoy for e in estado.empresas) / total_ventas
    else:
        calidad_media_transacción = sum(e.calidad for e in estado.empresas) / total_empresas if total_empresas > 0 else 0.0

    satisfacción_media = sum(e.satisfacción for e in estado.empresas) / total_empresas if total_empresas > 0 else 0.0
    
    total_ingreso_empresas = sum(
        getattr(e, "precio_venta_real", e.precio) * e.ventas_hoy 
        for e in estado.empresas
    )

    if total_ventas > 0:
        precio_transaccion_medio = total_ingreso_empresas / total_ventas
    else:
        precio_transaccion_medio = precio_lista_medio

    num_formales = sum(e.empleados_formales for e in estado.empresas)
    
    suma_salarios_formales = sum(
        getattr(e, "salario_pago_real", e.salario) * e.empleados_formales 
        for e in estado.empresas
    )

    num_informales = sum(e.empleados_informales for e in estado.empresas)
    
    suma_salarios_informales = sum(
        getattr(e, "salario_informal_pago_real", e.salario_informal) * e.empleados_informales 
        for e in estado.empresas
    )

    total_gasto_empresas = suma_salarios_formales + suma_salarios_informales

    salario_medio = suma_salarios_formales / num_formales if num_formales > 0 else 0.0
    salario_informal_medio = suma_salarios_informales / num_informales if num_informales > 0 else 0.0

    estado.estadisticas.salario_medio.append(
        salario_medio
    )
    estado.estadisticas.salario_informal_medio.append(
        salario_informal_medio
    )
    estado.estadisticas.precio_lista_medio.append(precio_lista_medio)
    estado.estadisticas.precio_transaccion_medio.append(precio_transaccion_medio)

    tasa_formal = num_formales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_informal = num_informales / total_trabajadores if total_trabajadores > 0 else 0.0
    tasa_desempleo = max(0.0, 1.0 - tasa_formal - tasa_informal)

    poder_de_compra_medio = (tasa_formal * salario_medio + tasa_informal * salario_informal_medio) / precio_lista_medio
    estado.poder_de_compra_medio = poder_de_compra_medio

    estado.presupuesto_medio_trabajadores = sum(t.presupuesto for t in estado.trabajadores) / total_trabajadores
    estado.sensibilidad_precio_medio = sum(t.sensibilidad_precio for t in estado.trabajadores) / total_trabajadores
    estado.sensibilidad_calidad_medio = sum(t.sensibilidad_calidad for t in estado.trabajadores) / total_trabajadores
    estado.sensibilidad_salario_medio = sum(t.sensibilidad_salario for t in estado.trabajadores) / total_trabajadores
    estado.sensibilidad_satisfacción_medio = sum(t.sensibilidad_satisfacción for t in estado.trabajadores) / total_trabajadores
    estado.productividad_medio_trabajadores = sum(t.productividad for t in estado.trabajadores) / total_trabajadores

    estado.presupuesto_medio_empresas = sum(e.presupuesto for e in estado.empresas) / total_empresas
    estado.calidad_medio = sum(e.calidad for e in estado.empresas) / total_empresas
    estado.satisfacción_medio = sum(e.satisfacción for e in estado.empresas) / total_empresas
    estado.productividad_medio_empresas = sum(e.productividad for e in estado.empresas) / total_empresas
    estado.productividad_objetivo_medio = sum(e.productividad_objetivo for e in estado.empresas) / total_empresas
    estado.tolerancia_medio = sum(e.tolerancia for e in estado.empresas) / total_empresas
    estado.probabilidad_venta_esperada_medio = sum(e.probabilidad_venta_esperada for e in estado.empresas) / total_empresas

    estado.estadisticas.empleo_formal.append(tasa_formal)
    estado.estadisticas.empleo_informal.append(tasa_informal)
    estado.estadisticas.desempleo.append(tasa_desempleo)

    estado.estadisticas.bienes_vendidos.append(float(total_ventas))
    estado.estadisticas.calidad_media.append(float(calidad_media_transacción))
    estado.estadisticas.satisfacción_media.append(float(satisfacción_media))
    estado.estadisticas.empresas_ingreso.append(float(total_ingreso_empresas))
    estado.estadisticas.empresas_gasto.append(float(total_gasto_empresas))

    estado.ventas_referencia = 0.99 * estado.ventas_referencia + 0.01 * float(total_ventas)
    estado.salario_referencia = 0.99 * estado.salario_referencia + 0.01 * salario_medio
    estado.salario_informal_referencia = 0.99 * estado.salario_informal_referencia + 0.01 * salario_informal_medio
    estado.precio_referencia = 0.99 * estado.precio_referencia + 0.01 * precio_lista_medio
    estado.poder_de_compra_referencia = 0.99 * estado.poder_de_compra_referencia + 0.01 * poder_de_compra_medio

    beneficio_esperado_medio = sum(e.beneficio_esperado for e in estado.empresas) / total_empresas
    estado.beneficio_esperado_medio = beneficio_esperado_medio
    estado.beneficio_esperado_referencia = 0.99 * estado.beneficio_esperado_referencia + 0.01 * beneficio_esperado_medio