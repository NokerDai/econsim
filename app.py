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

if "velocidad" not in st.session_state:
    st.session_state.velocidad = 1

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


def registrar_snapshots(snapshots):
    if not snapshots:
        return
    nuevos_datos = []
    for snap in snapshots:
        if snap.día not in st.session_state.historial.index:
            nuevos_datos.append({
                "Día": snap.día,
                "Salario": snap.salario_medio,
                "Salario informal": snap.salario_informal_medio,
                "Precio": snap.precio_medio
            })
    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos).set_index("Día")
        st.session_state.historial = pd.concat([st.session_state.historial, df_nuevos])


with st.sidebar:
    st.subheader("Salario mínimo")

    st.checkbox(
        "Salario mínimo automático",
        key="salario_mínimo_automático",
    )

    if st.session_state.salario_mínimo_automático != sim.config.salario_mínimo_automático:
        sim.config.salario_mínimo_automático = st.session_state.salario_mínimo_automático

    # Sincronizar sliders si el salario mínimo se controla automáticamente
    if st.session_state.salario_mínimo_automático:
        st.session_state.salario_slider = int(sim.config.salario_mínimo)
        st.session_state.salario_input = int(sim.config.salario_mínimo)

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

# Botones de control de ejecución de la simulación
col_btn1, col_btn2, col_btn3, col_vel = st.columns([1.5, 1.5, 1.5, 3])

with col_btn1:
    if st.session_state.auto_avance:
        if st.button("⏸ Pausar", use_container_width=True):
            st.session_state.auto_avance = False
            st.rerun()
    else:
        if st.button("▶ Iniciar", use_container_width=True):
            st.session_state.auto_avance = True
            st.rerun()

with col_btn2:
    if st.button("⏭ Día siguiente", disabled=st.session_state.auto_avance, use_container_width=True):
        if sim.step():
            registrar_snapshots([sim.obtener_snapshot()])
        st.rerun()

with col_btn3:
    if st.button("🔄 Reiniciar", use_container_width=True):
        sim.reset()
        st.session_state.historial = pd.DataFrame(
            columns=["Salario", "Salario informal", "Precio"]
        )
        st.session_state.historial.index.name = "Día"
        st.session_state.auto_avance = False
        st.rerun()

with col_vel:
    st.slider(
        "Velocidad (días por paso)",
        min_value=1,
        max_value=100,
        key="velocidad"
    )

st.divider()

run_every = 0.4 if st.session_state.auto_avance else None


@st.fragment(run_every=run_every)
def panel():

    if st.session_state.auto_avance:
        snapshots = []
        for _ in range(st.session_state.velocidad):
            if sim.step():
                snapshots.append(sim.obtener_snapshot())
            else:
                st.session_state.auto_avance = False
                break
        registrar_snapshots(snapshots)
        # Forzar un rerun del script principal si se detuvo el auto_avance
        if not st.session_state.auto_avance:
            st.rerun()

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
        # El gráfico muestra una ventana móvil de los últimos 365 días simulados
        último_día = st.session_state.historial.index.max()
        historial_filtrado = st.session_state.historial[
            st.session_state.historial.index > (último_día - 365)
        ]
        st.line_chart(historial_filtrado, height=420)
    else:
        st.info("Todavía no hay datos. Iniciá la simulación o avanzá un día.")


panel()