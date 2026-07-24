# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    num_trabajadores = max(len(estado.trabajadores), 1)
    num_empresas = max(len(estado.empresas), 1)

    ancla_trabajadores = min(config.num_trabajadores / num_trabajadores, 5)
    ancla_empresas = min(config.num_trabajadores / num_empresas, 5)

    poder = estado.poder_de_compra_medio
    ref = estado.poder_de_compra_referencia

    ############
    # Personas #
    ############
    if poder > ref * 1.05:
        for _ in range(round(ancla_trabajadores)):
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
    if poder < ref * 0.95:
        for _ in range(round(ancla_empresas)):
            nueva_empresa = Empresa.crear_inicial(config, rand)
            nueva_empresa.presupuesto = estado.presupuesto_medio_empresas * rand.uniform(0.85, 1.15)
            nueva_empresa.precio = estado.estadisticas.precio_lista_medio[-1] * rand.uniform(0.85, 1.15)
            nueva_empresa.salario = max(estado.estadisticas.salario_medio[-1] * rand.uniform(0.85, 1.15), config.salario_mínimo, 1.0)
            nueva_empresa.salario_informal = max(estado.estadisticas.salario_informal_medio[-1] * rand.uniform(0.85, 1.15), 1.0)
            nueva_empresa.calidad = estado.calidad_medio * rand.uniform(0.85, 1.15)
            nueva_empresa.satisfacción = estado.satisfacción_medio * rand.uniform(0.85, 1.15)
            nueva_empresa.productividad = estado.productividad_medio_empresas * rand.uniform(0.85, 1.15)
            nueva_empresa.productividad_objetivo = estado.productividad_objetivo_medio * rand.uniform(0.85, 1.15)
            nueva_empresa.tolerancia = estado.tolerancia_medio * rand.uniform(0.85, 1.15)
            estado.empresas.append(nueva_empresa)

    estado.empresas = [
        e for e in estado.empresas
        if not (
            (e.presupuesto < e.salario_informal and e.inventario == 0)
            or (e.días_sin_vender > 180 and rand.random() < 0.10)
        )
    ]

    estado.trabajadores = [
        t for t in estado.trabajadores
        if not (
            t.días_sin_comprar > 30 and rand.random() < 0.10
        )
    ]