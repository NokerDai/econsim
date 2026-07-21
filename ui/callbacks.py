# ui/callbacks.py
import streamlit as st
from ui.salario_utils import resolver_valor_salario

def sincronizar_salario_slider(sim):
    val = st.session_state._salario_slider
    st.session_state.salario_slider = val
    st.session_state.salario_input = val
    st.session_state._salario_input = val
    sim.cambiar_salario_mínimo(val)

def sincronizar_salario_input(sim):
    val = st.session_state._salario_input
    st.session_state.salario_slider = val
    st.session_state.salario_input = val
    st.session_state._salario_slider = val
    sim.cambiar_salario_mínimo(val)

def sincronizar_salario_mínimo_automático(sim):
    val = st.session_state._salario_mínimo_automático
    st.session_state.salario_mínimo_automático = val
    sim.config.salario_mínimo_automático = val
    if val:
        val_sal = int(sim.config.salario_mínimo or 0)
        st.session_state.salario_slider = val_sal
        st.session_state.salario_input = val_sal
        st.session_state._salario_slider = val_sal
        st.session_state._salario_input = val_sal
    else:
        valor_salario = resolver_valor_salario(
            False,
            st.session_state.salario_slider,
            st.session_state.salario_input,
            sim.config.salario_mínimo,
        )
        st.session_state.salario_slider = valor_salario
        st.session_state.salario_input = valor_salario
        st.session_state._salario_slider = valor_salario
        st.session_state._salario_input = valor_salario
        sim.cambiar_salario_mínimo(valor_salario)

def sincronizar_informalidad_por_empresa_slider(sim):
    val = st.session_state._informalidad_por_empresa_slider
    st.session_state.informalidad_por_empresa_slider = val
    st.session_state.informalidad_por_empresa_input = val
    st.session_state._informalidad_por_empresa_input = val
    sim.cambiar_informalidad_por_empresa(val)

def sincronizar_informalidad_por_empresa_input(sim):
    val = st.session_state._informalidad_por_empresa_input
    st.session_state.informalidad_por_empresa_slider = val
    st.session_state.informalidad_por_empresa_input = val
    st.session_state._informalidad_por_empresa_slider = val
    sim.cambiar_informalidad_por_empresa(val)

def sincronizar_tasa(sim):
    val = float(st.session_state._tasa_slider)
    st.session_state.tasa_slider = val
    sim.config.tasa_salario_mínimo = val

def sincronizar_formalidad_límite(sim):
    val = float(st.session_state._formalidad_límite_slider)
    st.session_state.formalidad_límite_slider = val
    sim.config.salario_mínimo_automático_formalidad_límite = val

def sincronizar_velocidad_slider(sim):
    valor = max(1, int(st.session_state._velocidad_slider))
    st.session_state.velocidad = valor
    st.session_state.velocidad_slider = valor
    st.session_state.velocidad_input = valor
    st.session_state._velocidad_input = valor
    st.session_state._velocidad_ui = valor
    sim.cambiar_velocidad(valor)

def sincronizar_velocidad_input(sim):
    valor = max(1, int(st.session_state._velocidad_input))
    st.session_state.velocidad = valor
    st.session_state.velocidad_slider = valor
    st.session_state.velocidad_input = valor
    st.session_state._velocidad_slider = valor
    st.session_state._velocidad_ui = valor
    sim.cambiar_velocidad(valor)

def sincronizar_tasa_emisión_slider(sim):
    val = st.session_state._tasa_emisión_slider
    st.session_state.tasa_emisión_slider = val
    st.session_state.tasa_emisión_input = val
    st.session_state._tasa_emisión_input = val
    sim.cambiar_tasa_emisión(val)

def sincronizar_tasa_emisión_input(sim):
    val = st.session_state._tasa_emisión_input
    st.session_state.tasa_emisión_slider = val
    st.session_state.tasa_emisión_input = val
    st.session_state._tasa_emisión_slider = val
    sim.cambiar_tasa_emisión(val)

def aplicar_productividad_formal(sim, valor):
    if hasattr(sim, "cambiar_productividad_formal"):
        sim.cambiar_productividad_formal(valor)
    else:
        sim.config.productividad_formal = float(valor)

def aplicar_productividad_informal(sim, valor):
    if hasattr(sim, "cambiar_productividad_informal"):
        sim.cambiar_productividad_informal(valor)
    else:
        sim.config.productividad_informal = float(valor)

def sincronizar_productividad_formal_slider(sim):
    val = st.session_state._productividad_formal_slider
    st.session_state.productividad_formal_slider = val
    st.session_state.productividad_formal_input = val
    st.session_state._productividad_formal_input = val
    aplicar_productividad_formal(sim, val)

def sincronizar_productividad_formal_input(sim):
    val = st.session_state._productividad_formal_input
    st.session_state.productividad_formal_slider = val
    st.session_state.productividad_formal_input = val
    st.session_state._productividad_formal_slider = val
    aplicar_productividad_formal(sim, val)

def sincronizar_productividad_informal_slider(sim):
    val = st.session_state._productividad_informal_slider
    st.session_state.productividad_informal_slider = val
    st.session_state.productividad_informal_input = val
    st.session_state._productividad_informal_input = val
    aplicar_productividad_informal(sim, val)

def sincronizar_productividad_informal_input(sim):
    val = st.session_state._productividad_informal_input
    st.session_state.productividad_informal_slider = val
    st.session_state.productividad_informal_input = val
    st.session_state._productividad_informal_slider = val
    aplicar_productividad_informal(sim, val)