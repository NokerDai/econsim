import streamlit as st
import pandas as pd

from config import Config
from simulation import Simulación


st.set_page_config(
    page_title="Simulación económica",
    page_icon="📈",
    layout="wide",
)


# --- Estado de sesión --- 
# Cada sesión de Streamlit tiene su propia Simulación independiente,
# igual que si cada usuario abriera su propia ventana de escritorio.

if "simulación" not in st.session_state:
    st.session_state.simulación = Simulación(Config())

if "auto_avance" not in st.session_state:
    st.session_state.auto_avance = False

if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=["Salario", "Precio"])
    st.session_state.historial.index.name = "Día"


sim = st.session_state.simulación


def registrar_snapshot():
    snapshot = sim.obtener_snapshot()
    st.session_state.historial.loc[snapshot.día] = [
        snapshot.salario_medio,
        snapshot.precio_medio,
    ]
    # Conservar solo los últimos 365 días simulados. Se filtra por el valor
    # del día (no por cantidad de filas), porque con auto-avance cada fila
    # puede representar un salto de varios días ("Velocidad"), y recortar
    # por cantidad de filas terminaba dejando ventanas de miles de días.
    último_día = st.session_state.historial.index.max()
    st.session_state.historial = st.session_state.historial[
        st.session_state.historial.index > último_día - 365
    ]


def alternar_auto_avance():
    st.session_state.auto_avance = not st.session_state.auto_avance


def avanzar_un_día():
    sim.step()
    registrar_snapshot()


def reiniciar():
    sim.reset()
    st.session_state.auto_avance = False
    st.session_state.historial = pd.DataFrame(columns=["Salario", "Precio"])
    st.session_state.historial.index.name = "Día"


# --- Barra lateral: controles ---

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
        disabled=not st.session_state.auto_avance,
    )

    st.divider()

    salario_mínimo = st.slider(
        "Salario mínimo",
        min_value=0,
        max_value=10000,
        value=int(sim.config.salario_mínimo),
    )
    if salario_mínimo != sim.config.salario_mínimo:
        sim.cambiar_salario_mínimo(salario_mínimo)

    emisión_diaria = st.slider(
        "Emisión monetaria diaria",
        min_value=0,
        max_value=100000,
        value=int(sim.config.emisión_diaria),
    )
    if emisión_diaria != sim.config.emisión_diaria:
        sim.cambiar_emisión(emisión_diaria)

    st.caption(
        f"{sim.config.num_trabajadores} trabajadores · "
        f"{sim.config.num_empresas} empresas"
    )


st.title("📈 Simulación económica")

# El intervalo del fragment solo está activo mientras "auto_avance" esté
# encendido; si no, run_every=None y el panel se queda quieto (equivalente
# a pausar el hilo en la versión de escritorio).
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

    col_día, col_salario, col_precio = st.columns(3)

    col_día.metric("Día", sim.estado.día)

    col_salario.metric(
        "Salario medio",
        f"{st.session_state.historial['Salario'].iloc[-1]:.2f}" if hay_datos else "—",
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
