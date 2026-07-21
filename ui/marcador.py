from typing import Any, Mapping


def esta_activa(dia_marcado: int, dia_actual: int, ventana_dias: int = 1000) -> bool:
    if dia_marcado is None:
        return False

    dia_marcado = int(dia_marcado)
    dia_actual = int(dia_actual)

    if dia_marcado < 0:
        return False

    if dia_marcado > dia_actual:
        return False

    return (dia_actual - dia_marcado) <= ventana_dias


def construir_texto_marcado(valores: Mapping[str, Any], separador: str = " | ") -> str:
    if not valores:
        return "Marca"

    partes = []
    for nombre, valor in valores.items():
        if isinstance(valor, float):
            if valor.is_integer():
                valor = int(valor)
            else:
                valor = round(valor, 4)
        partes.append(f"{nombre}={valor}")

    return separador.join(partes)


def obtener_valores_marcado(sim, session_state):
    return {
        "Día": int(session_state.get("marcador_dia", getattr(sim.estado, "día", 0))),
        "Salario mínimo": float(sim.config.salario_mínimo),
        "Informalidad": float(sim.config.informalidad_por_empresa),
        "Productividad formal": float(sim.config.productividad_formal),
        "Productividad informal": float(sim.config.productividad_informal),
        "Tasa emisión": float(sim.config.tasa_emisión),
        "Velocidad": int(getattr(sim.config, "velocidad", 0)),
    }
