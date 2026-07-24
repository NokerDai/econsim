# --- demografía.py ---
from .trabajador import Trabajador
from .empresa import Empresa

def demografía_y_firmas(estado):
    config = estado.config
    rand = estado.aleatorio
    num_trabajadores = max(len(estado.trabajadores), 1)
    num_empresas = max(len(estado.empresas), 1)

    poder = estado.poder_de_compra_medio
    poder_ref = estado.poder_de_compra_referencia

    beneficio_esperado = estado.beneficio_esperado_medio
    beneficio_ref = estado.beneficio_esperado_referencia

    ratio = config.num_trabajadores / config.num_empresas
    ancla_trabajadores = min(config.num_trabajadores / num_trabajadores, 5 * ratio)
    ancla_empresas = min(config.num_empresas / num_empresas, 5)

    ratio_trabajadores = poder / poder_ref
    ratio_empresas = beneficio_esperado / beneficio_ref

    exceso_trabajadores = max(0.0, ratio_trabajadores - 1.05)
    cantidad_trabajadores = min(round(ancla_trabajadores * exceso_trabajadores * 5), 2)

    exceso_empresas = max(0.0, ratio_empresas - 1.05)
    cantidad_empresas = min(round(ancla_empresas * exceso_empresas * 5), 2)

    ############
    # Personas #
    ############
    if poder > poder_ref * 1.1:
        for _ in range(cantidad_trabajadores):
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
    if beneficio_esperado > beneficio_ref * 1.1:
        for _ in range(cantidad_empresas):
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
            nueva_empresa.probabilidad_venta_esperada = min(estado.probabilidad_venta_esperada_medio * rand.uniform(0.85, 1.15), 1.0)
            nueva_empresa.beneficio_esperado = estado.beneficio_esperado_medio * rand.uniform(0.85, 1.15)
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