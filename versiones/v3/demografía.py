# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    ############
    # Personas #
    ############
    if estado.poder_de_compra_medio > estado.poder_de_compra_referencia:
        nuevo_trabajador = Trabajador.crear_inicial(config, rand)
        nuevo_trabajador.presupuesto = estado.presupuesto_medio_trabajadores * rand.uniform(0.85, 1.15)
        nuevo_trabajador.sensibilidad_precio = estado.sensibilidad_precio_medio * rand.uniform(0.85, 1.15)
        nuevo_trabajador.sensibilidad_calidad = estado.sensibilidad_calidad_medio * rand.uniform(0.85, 1.15)
        nuevo_trabajador.sensibilidad_salario = estado.sensibilidad_salario_medio * rand.uniform(0.85, 1.15)
        nuevo_trabajador.sensibilidad_satisfacción = estado.sensibilidad_satisfacción_medio * rand.uniform(0.85, 1.15)
        nuevo_trabajador.productividad = estado.productividad_medio_trabajadores * rand.uniform(0.85, 1.15)
        estado.trabajadores.append(nuevo_trabajador)

    ############
    # Empresas #
    ############
    if estado.poder_de_compra_medio < estado.poder_de_compra_referencia:
        nueva_empresa = Empresa.crear_inicial(config, rand)
        nueva_empresa.presupuesto = estado.presupuesto_medio_empresas * rand.uniform(0.85, 1.15)
        nueva_empresa.precio = estado.precio_lista_medio * rand.uniform(0.85, 1.15)
        nueva_empresa.salario = max(estado.salario_medio * rand.uniform(0.85, 1.15), config.salario_mínimo, 1.0)
        nueva_empresa.salario_informal = max(estado.salario_informal_medio * rand.uniform(0.85, 1.15), 1.0)
        nueva_empresa.calidad = estado.calidad_medio * rand.uniform(0.85, 1.15)
        nueva_empresa.satisfacción = estado.satisfacción_medio * rand.uniform(0.85, 1.15)
        nueva_empresa.productividad = estado.productividad_medio_empresas * rand.uniform(0.85, 1.15)
        nueva_empresa.productividad_objetivo = estado.productividad_objetivo_medio * rand.uniform(0.85, 1.15)
        nueva_empresa.tolerancia = estado.tolerancia_medio * rand.uniform(0.85, 1.15)
        estado.empresas.append(nueva_empresa)

    for e in estado.empresas:
        if (e.presupuesto < e.salario_informal and e.inventario == 0) or (e.días_sin_vender > 180 and rand.random < 0.10):
            estado.empresas.remove(e)
    for t in estado.trabajadores:
        if t.días_sin_comprar > 10 and rand.random < 0.10:
            estado.trabajadores.remove(e)