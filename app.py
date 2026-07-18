# --- app.py ---
import streamlit as st
import pandas as pd

from config import Config
from simulation import Simulación
from salario_utils import resolver_valor_salario


st.set_page_config(
    page_title="Simulación económica",
    page_icon="📈",
    layout="wide",
)


st.markdown(
    """
    <style>
    /* Ocultar botones de subir/bajar de Streamlit */
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }
    /* Quitar el espaciado derecho de los botones eliminados */
    div[data-testid="stNumberInput"] input {
        padding-right: 1rem !important;
    }
    /* Ocultar botones de incremento nativos del navegador */
    div[data-testid="stNumberInput"] input[type=number]::-webkit-inner-spin-button, 
    div[data-testid="stNumberInput"] input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }
    div[data-testid="stNumberInput"] input[type=number] {
        -moz-appearance: textfield;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "simulación" not in st.session_state:
    st.session_state.simulación = Simulación(Config())

if "auto_avance" not in st.session_state:
    st.session_state.auto_avance = False

if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(
        columns=[
            "Salario",
            "Salario informal",
            "Precio",
            "Desempleo"
        ]
    ).astype(float)
    st.session_state.historial.index.name = "Día"


sim = st.session_state.simulación


# Estado de controles
if "salario_mínimo_automático" not in st.session_state:
    st.session_state.salario_mínimo_automático = sim.config.salario_mínimo_automático


if "salario_slider" not in st.session_state:
    st.session_state.salario_slider = int(sim.config.salario_mínimo or 0)

if "salario_input" not in st.session_state:
    st.session_state.salario_input = int(sim.config.salario_mínimo or 0)


if "informalidad_por_empresa_slider" not in st.session_state:
    st.session_state.informalidad_por_empresa_slider = int(sim.config.informalidad_por_empresa)

if "informalidad_por_empresa_input" not in st.session_state:
    st.session_state.informalidad_por_empresa_input = int(sim.config.informalidad_por_empresa)


if "tasa_slider" not in st.session_state:
    st.session_state.tasa_slider = 0.3
    sim.config.tasa_salario_mínimo = 0.3

if "velocidad_slider" not in st.session_state:
    st.session_state.velocidad_slider = max(1, int(getattr(sim.config, "velocidad", 1)))

if "velocidad_input" not in st.session_state:
    st.session_state.velocidad_input = max(1, int(getattr(sim.config, "velocidad", 1)))

if "velocidad" not in st.session_state:
    st.session_state.velocidad = max(1, int(getattr(sim.config, "velocidad", 1)))

if "tasa_emisión_slider" not in st.session_state:
    st.session_state.tasa_emisión_slider = float(sim.config.tasa_emisión)

if "tasa_emisión_input" not in st.session_state:
    st.session_state.tasa_emisión_input = float(sim.config.tasa_emisión)


def sincronizar_salario_slider():
    st.session_state.salario_input = st.session_state.salario_slider
    sim.cambiar_salario_mínimo(st.session_state.salario_slider)


def sincronizar_salario_input():
    st.session_state.salario_slider = st.session_state.salario_input
    sim.cambiar_salario_mínimo(st.session_state.salario_input)


def sincronizar_informalidad_por_empresa_slider():
    st.session_state.informalidad_por_empresa_input = st.session_state.informalidad_por_empresa_slider
    sim.cambiar_informalidad_por_empresa(st.session_state.informalidad_por_empresa_slider)


def sincronizar_informalidad_por_empresa_input():
    st.session_state.informalidad_por_empresa_slider = st.session_state.informalidad_por_empresa_input
    sim.cambiar_informalidad_por_empresa(st.session_state.informalidad_por_empresa_input)


def sincronizar_tasa():
    st.session_state.tasa_slider = float(st.session_state.tasa_slider)
    sim.config.tasa_salario_mínimo = st.session_state.tasa_slider


def sincronizar_velocidad_slider():
    st.session_state.velocidad_input = st.session_state.velocidad_slider
    st.session_state.velocidad = max(1, int(st.session_state.velocidad_slider))
    sim.cambiar_velocidad(st.session_state.velocidad)


def sincronizar_velocidad_input():
    st.session_state.velocidad_slider = st.session_state.velocidad_input
    st.session_state.velocidad = max(1, int(st.session_state.velocidad_input))
    sim.cambiar_velocidad(st.session_state.velocidad)


def sincronizar_tasa_emisión_slider():
    st.session_state.tasa_emisión_input = st.session_state.tasa_emisión_slider
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_slider)


def sincronizar_tasa_emisión_input():
    st.session_state.tasa_emisión_slider = st.session_state.tasa_emisión_input
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_input)


def registrar_snapshots(snapshots):
    if not snapshots:
        return
    nuevos_datos = []
    for snap in snapshots:
        if snap.día not in st.session_state.historial.index:
            nuevos_datos.append({
                "Día": int(snap.día),
                "Salario": float(snap.salario_medio),
                "Salario informal": float(snap.salario_informal_medio),
                "Precio": float(snap.precio_medio),
            })
    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos).set_index("Día").astype(float)
        st.session_state.historial = pd.concat([st.session_state.historial, df_nuevos])


with st.sidebar:
    st.subheader("Control de ejecución")

    col_btn1, col_btn2 = st.columns(2)
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
        if st.button("⏭ Día", disabled=st.session_state.auto_avance, use_container_width=True):
            if sim.step():
                registrar_snapshots([sim.obtener_snapshot()])
            st.rerun()

    if st.button("🔄 Reiniciar", use_container_width=True):
        sim.reset()
        st.session_state.historial = pd.DataFrame(
            columns=[
                "Salario",
                "Salario informal",
                "Precio",
            ]
        ).astype(float)
        st.session_state.historial.index.name = "Día"
        st.session_state.auto_avance = False
        st.rerun()

    st.slider(
        "Velocidad (días por paso)",
        min_value=1,
        max_value=1000,
        key="velocidad_slider",
        value=st.session_state.velocidad_slider,
        on_change=sincronizar_velocidad_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=1,
        max_value=1000,
        step=1,
        key="velocidad_input",
        value=st.session_state.velocidad_input,
        on_change=sincronizar_velocidad_input,
    )

    st.divider()

    st.checkbox(
        "Salario mínimo automático",
        key="salario_mínimo_automático",
    )

    if st.session_state.salario_mínimo_automático != sim.config.salario_mínimo_automático:
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

    # Creamos un marcador de posición que se actualizará de forma dinámica
    salario_metric_placeholder = st.empty()

    if st.session_state.salario_mínimo_automático:
        salario_metric_placeholder.metric("Valor actual calculado", f"{sim.config.salario_mínimo:.2f}")
        st.slider(
            "Tasa de salario mínimo",
            min_value=0.0,
            max_value=2.0,
            step=0.01,
            key="tasa_slider",
            value=st.session_state.tasa_slider,
            on_change=sincronizar_tasa,
        )
    else:
        salario_metric_placeholder.empty()
        st.slider(
            "Salario mínimo",
            min_value=0,
            max_value=10000,
            key="salario_slider",
            on_change=sincronizar_salario_slider,
        )

        st.number_input(
            "Valor exacto",
            min_value=0,
            max_value=10000,
            step=1,
            key="salario_input",
            on_change=sincronizar_salario_input,
        )


    st.slider(
        "Informalidad por empresa",
        min_value=0,
        max_value=100,
        key="informalidad_por_empresa_slider",
        on_change=sincronizar_informalidad_por_empresa_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0,
        max_value=100,
        step=1,
        key="informalidad_por_empresa_input",
        on_change=sincronizar_informalidad_por_empresa_input,
    )


    st.divider()

    st.slider(
        "Tasa emisión",
        min_value=-1.0,
        max_value=1.0,
        step=0.01,
        key="tasa_emisión_slider",
        on_change=sincronizar_tasa_emisión_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=-1.0,
        max_value=1.0,
        step=0.01,
        key="tasa_emisión_input",
        on_change=sincronizar_tasa_emisión_input,
    )


st.title("📈 Simulación económica")

run_every = 1 if st.session_state.auto_avance else None


@st.fragment(run_every=run_every)
def panel():

    if st.session_state.auto_avance:
        snapshots = []
        for _ in range(int(st.session_state.velocidad)):
            if sim.step():
                snapshots.append(sim.obtener_snapshot())
            else:
                st.session_state.auto_avance = False
                break
        registrar_snapshots(snapshots)
        # Forzar un rerun del script principal si se detuvo el auto_avance
        if not st.session_state.auto_avance:
            st.rerun()

    # Actualizar dinámicamente solo el elemento de texto métrico en la barra lateral
    if st.session_state.salario_mínimo_automático:
        salario_metric_placeholder.metric("Valor actual calculado", f"{sim.config.salario_mínimo:.2f}")

    hay_datos = len(st.session_state.historial) > 0

    # ---------------------------------------------------------
    # 1. TARJETAS / MÉTRICAS SUPERIORES
    # ---------------------------------------------------------
    col_día, col_salario, col_salario_inf, col_precio = st.columns(4)

    col_día.metric("Día", sim.estado.día)

    col_salario.metric(
        "Salario medio",
        f"{st.session_state.historial['Salario'].iloc[-1]:.2f}" if hay_datos else "—",
    )

    col_precio.metric(
        "Precio medio",
        f"{st.session_state.historial['Precio'].iloc[-1]:.2f}" if hay_datos else "—",
    )

    # ---------------------------------------------------------
    # 2. LOS TRES GRÁFICOS APILADOS UNO DEBAJO DEL OTRO
    # ---------------------------------------------------------
    if hay_datos:
        # Filtrar la ventana móvil de los últimos 365 días simulados
        último_día = st.session_state.historial.index.max()
        historial_filtrado = st.session_state.historial[
            st.session_state.historial.index > (último_día - 365)
        ].astype(float)

        # Gráfico 2: Evolución de Salarios
        st.subheader("1. Evolución de Salarios")
        st.line_chart(
            historial_filtrado[["Salario", "Salario informal"]],
            height=300
        )

        # Gráfico 3: Evolución de Precios
        st.subheader("2. Evolución del Precio Medio")
        st.line_chart(
            historial_filtrado[["Precio"]],
            height=300
        )

    else:
        st.info("Todavía no hay datos. Iniciá la simulación o avanzá un día.")


panel()