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


# Estado de controles sincronizados
if "salario_slider" not in st.session_state:
    st.session_state.salario_slider = int(sim.config.salario_mínimo)

if "salario_input" not in st.session_state:
    st.session_state.salario_input = int(sim.config.salario_mínimo)

if "emision_slider" not in st.session_state:
    st.session_state.emision_slider = int(sim.config.emisión_diaria)

if "emision_input" not in st.session_state:
    st.session_state.emision_input = int(sim.config.emisión_diaria)


def sync_salario_slider():
    st.session_state.salario_input = st.session_state.salario_slider
    sim.cambiar_salario_mínimo(st.session_state.salario_slider)


def sync_salario_input():
    st.session_state.salario_slider = st.session_state.salario_input
    sim.cambiar_salario_mínimo(st.session_state.salario_input)


def sync_emision_slider():
    st.session_state.emision_input = st.session_state.emision_slider
    sim.cambiar_emisión(st.session_state.emision_slider)


def sync_emision_input():
    st.session_state.emision_slider = st.session_state.emision_input
    sim.cambiar_emisión(st.session_state.emision_input)


def registrar_snapshot():
    snapshot = sim.obtener_snapshot()

    st.session_state.historial.loc[snapshot.día] = [
        snapshot.salario_medio,
        snapshot.salario_informal_medio,
        snapshot.precio_medio,
    ]

    ultimo_día = st.session_state.historial.index.max()
    st.session_state.historial = st.session_state.historial[
        st.session_state.historial.index > ultimo_día - 365
    ]


def alternar_auto_avance():
    st.session_state.auto_avance = not st.session_state.auto_avance


def avanzar_un_día():
    sim.step()
    registrar_snapshot()


def reiniciar():
    sim.reset()
    st.session_state.auto_avance = False
    st.session_state.historial = pd.DataFrame(
        columns=["Salario", "Salario informal", "Precio"]
    )
    st.session_state.historial.index.name = "Día"

    st.session_state.salario_slider = int(sim.config.salario_mínimo)
    st.session_state.salario_input = int(sim.config.salario_mínimo)
    st.session_state.emision_slider = int(sim.config.emisión_diaria)
    st.session_state.emision_input = int(sim.config.emisión_diaria)


with st.sidebar:
    st.header("Controles")

    col1, col2 = st.columns(2)

    col1.button(
        "⏸️ Pausar" if st.session_state.auto_avance else "▶️ Iniciar",
        on_click=alternar_auto_avance,
        use_container_width=True,
    )

    col2.button(
        "⏭️ Día siguiente",
        on_click=avanzar_un_día,
        disabled=st.session_state.auto_avance,
        use_container_width=True,
    )

    st.button("🔄 Reiniciar", on_click=reiniciar, use_container_width=True)

    st.divider()

    velocidad = st.slider(
        "Velocidad (días por actualización)",
        min_value=1,
        max_value=50,
        value=5,
    )

    st.divider()

    st.subheader("Salario mínimo")

    st.slider(
        "Salario mínimo",
        min_value=0,
        max_value=10000,
        key="salario_slider",
        on_change=sync_salario_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0,
        max_value=10000,
        step=1,
        key="salario_input",
        on_change=sync_salario_input,
    )

    st.divider()

    st.subheader("Emisión monetaria diaria")

    st.slider(
        "Emisión monetaria diaria",
        min_value=0,
        max_value=100000,
        key="emision_slider",
        on_change=sync_emision_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0,
        max_value=100000,
        step=100,
        key="emision_input",
        on_change=sync_emision_input,
    )

    st.caption(
        f"{sim.config.num_trabajadores} trabajadores · "
        f"{sim.config.num_empresas} empresas"
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
