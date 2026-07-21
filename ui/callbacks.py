# ui/callbacks.py
import streamlit as st
from ui.salario_utils import resolver_valor_salario

def sincronizar_salario_slider(sim):
    st.session_state.salario_input = st.session_state.salario_slider
    sim.cambiar_salario_mínimo(st.session_state.salario_slider)

def sincronizar_salario_input(sim):
    st.session_state.salario_slider = st.session_state.salario_input
    sim.cambiar_salario_mínimo(st.session_state.salario_input)

def sincronizar_salario_mínimo_automático(sim):
    sim.config.salario_mínimo_automático = st.session_state.salario_mínimo_automático
    if st.session_state.salario_mínimo_automático:
        st.session_state.salario_slider = int(sim.config.salario_mínimo or 0)
        st.session_state.salario_input = int(sim.config.salario_mínimo or 0)
    else:
        valor_salario = resolver_valor_salario(
            False,
            st.session_state.salario_slider,
            st.session_state.salario_input,
            sim.config.salario_mínimo,
        )
        st.session_state.salario_slider = valor_salario
        st.session_state.salario_input = valor_salario
        sim.cambiar_salario_mínimo(valor_salario)

def sincronizar_informalidad_por_empresa_slider(sim):
    st.session_state.informalidad_por_empresa_input = st.session_state.informalidad_por_empresa_slider
    sim.cambiar_informalidad_por_empresa(st.session_state.informalidad_por_empresa_slider)

def sincronizar_informalidad_por_empresa_input(sim):
    st.session_state.informalidad_por_empresa_slider = st.session_state.informalidad_por_empresa_input
    sim.cambiar_informalidad_por_empresa(st.session_state.informalidad_por_empresa_input)

def sincronizar_tasa(sim):
    st.session_state.tasa_slider = float(st.session_state.tasa_slider)
    sim.config.tasa_salario_mínimo = st.session_state.tasa_slider

def sincronizar_velocidad_slider(sim):
    valor = max(1, int(st.session_state.velocidad_slider))
    st.session_state.velocidad = valor
    st.session_state.velocidad_input = valor
    st.session_state._velocidad_ui = valor
    sim.cambiar_velocidad(valor)

def sincronizar_velocidad_input(sim):
    valor = max(1, int(st.session_state.velocidad_input))
    st.session_state.velocidad = valor
    st.session_state.velocidad_slider = valor
    st.session_state._velocidad_ui = valor
    sim.cambiar_velocidad(valor)

def sincronizar_tasa_emisión_slider(sim):
    st.session_state.tasa_emisión_input = st.session_state.tasa_emisión_slider
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_slider)

def sincronizar_tasa_emisión_input(sim):
    st.session_state.tasa_emisión_slider = st.session_state.tasa_emisión_input
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_input)

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
    st.session_state.productividad_formal_input = st.session_state.productividad_formal_slider
    aplicar_productividad_formal(sim, st.session_state.productividad_formal_slider)

def sincronizar_productividad_formal_input(sim):
    st.session_state.productividad_formal_slider = st.session_state.productividad_formal_input
    aplicar_productividad_formal(sim, st.session_state.productividad_formal_input)

def sincronizar_productividad_informal_slider(sim):
    st.session_state.productividad_informal_input = st.session_state.productividad_informal_slider
    aplicar_productividad_informal(sim, st.session_state.productividad_informal_slider)

def sincronizar_productividad_informal_input(sim):
    st.session_state.productividad_informal_slider = st.session_state.productividad_informal_input
    aplicar_productividad_informal(sim, st.session_state.productividad_informal_input)