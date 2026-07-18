import streamlit as st
import pandas as pd

from config import Config
from simulation import Simulación


st.set_page_config(
    page_title="Simulación económica",
    page_icon="📈",
    layout="wide",
)


if "simulación" not in st.session_state:
    st.session_state.simulación = Simulación(Config())

if "auto_avance" not in st.session_state:
    st.session_state.auto_avance = False

if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(
        columns=["Salario", "Salario informal", "Precio"]
    )
    st.session_state.historial.index.name = "Día"

sim = st.session_state.simulación


# Estado de controles
if "salario_mínimo_automático" not in st.session_state:
    st.session_state.salario_mínimo_automático = sim.config.salario_mínimo_automático


if "salario_slider" not in st.session_state:
    st.session_state.salario_slider = int(sim.config.salario_mínimo)

if "salario_input" not in st.session_state:
    st.session_state.salario_input = int(sim.config.salario_mínimo)


if "emisión_slider" not in st.session_state:
    st.session_state.emisión_slider = int(sim.config.emisión_diaria)

if "emisión_input" not in st.session_state:
    st.session_state.emisión_input = int(sim.config.emisión_diaria)


def sincronizar_salario_slider():
    st.session_state.salario_input = st.session_state.salario_slider
    sim.cambiar_salario_mínimo(st.session_state.salario_slider)


def sincronizar_salario_input():
    st.session_state.salario_slider = st.session_state.salario_input
    sim.cambiar_salario_mínimo(st.session_state.salario_input)


def sincronizar_emisión_slider():
    st.session_state.emisión_input = st.session_state.emisión_slider
    sim.cambiar_emisión(st.session_state.emisión_slider)


def sincronizar_emisión_input():
    st.session_state.emisión_slider = st.session_state.emisión_input
    sim.cambiar_emisión(st.session_state.emisión_input)


with st.sidebar:
    st.subheader("Salario mínimo")

    st.checkbox(
        "Salario mínimo automático",
        key="salario_mínimo_automático",
    )

    if st.session_state.salario_mínimo_automático != sim.config.salario_mínimo_automático:
        sim.config.salario_mínimo_automático = st.session_state.salario_mínimo_automático


    st.slider(
        "Salario mínimo",
        min_value=0,
        max_value=10000,
        key="salario_slider",
        disabled=st.session_state.salario_mínimo_automático,
        on_change=sincronizar_salario_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0,
        max_value=10000,
        step=1,
        key="salario_input",
        disabled=st.session_state.salario_mínimo_automático,
        on_change=sincronizar_salario_input,
    )


    st.divider()

    st.subheader("Emisión monetaria diaria")

    st.slider(
        "Emisión monetaria diaria",
        min_value=0,
        max_value=100000,
        key="emisión_slider",
        on_change=sincronizar_emisión_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0,
        max_value=100000,
        step=100,
        key="emisión_input",
        on_change=sincronizar_emisión_input,
    )


st.title("📈 Simulación económica")

run_every = 0.4 if st.session_state.auto_avance else None


@st.fragment(run_every=run_every)
def panel():

    if st.session_state.auto_avance:
        for _ in range(velocidad):
            if not sim.step():
                st.session_state.auto_avance = False
                break
        registrar_snapshot()

    hay_datos = len(st.session_state.historial) > 0

    col_día, col_salario, col_salario_informal, col_precio = st.columns(4)

    col_día.metric("Día", sim.estado.día)

    col_salario.metric(
        "Salario medio",
        f"{st.session_state.historial['Salario'].iloc[-1]:.2f}" if hay_datos else "—",
    )

    col_salario_informal.metric(
        "Salario informal medio",
        f"{st.session_state.historial['Salario informal'].iloc[-1]:.2f}" if hay_datos else "—",
    )

    col_precio.metric(
        "Precio medio",
        f"{st.session_state.historial['Precio'].iloc[-1]:.2f}" if hay_datos else "—",
    )

    if hay_datos:
        st.line_chart(st.session_state.historial, height=420)
    else:
        st.info("Todavía no hay datos. Iniciá la simulación o avanzá un día.")


panel()