# --- app.py ---
import streamlit as st
import pandas as pd
import time

from config import Config
from simulation import Simulación
from salario_utils import resolver_valor_salario
from marcador import construir_texto_marcado, esta_activa, obtener_valores_marcado


st.set_page_config(
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

sim = st.session_state.simulación

if "velocidad" not in st.session_state:
    st.session_state.velocidad = max(
        1,
        int(getattr(sim.config, "velocidad", 1))
    )

if "_velocidad_ui" not in st.session_state:
    st.session_state._velocidad_ui = st.session_state.velocidad

if "auto_avance" not in st.session_state:
    st.session_state.auto_avance = False

if "ajuste_velocidad_automatico" not in st.session_state:
    st.session_state.ajuste_velocidad_automatico = False

if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(
        columns=[
            "Salario",
            "Salario informal",
            "Precio",
            "Empleo formal",
            "Empleo informal",
            "Desempleo"
        ]
    ).astype(float)
    st.session_state.historial.index.name = "Día"

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

if "marcador_dia" not in st.session_state:
    st.session_state.marcador_dia = max(0, int(getattr(sim.estado, "día", 0)))

if "productividad_formal_slider" not in st.session_state:
    st.session_state.productividad_formal_slider = float(sim.config.productividad_formal)

if "productividad_formal_input" not in st.session_state:
    st.session_state.productividad_formal_input = float(sim.config.productividad_formal)

if "productividad_informal_slider" not in st.session_state:
    st.session_state.productividad_informal_slider = float(sim.config.productividad_informal)

if "productividad_informal_input" not in st.session_state:
    st.session_state.productividad_informal_input = float(sim.config.productividad_informal)


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
    valor = max(1, int(st.session_state.velocidad_slider))

    st.session_state.velocidad = valor
    st.session_state.velocidad_input = valor
    st.session_state._velocidad_ui = valor

    sim.cambiar_velocidad(valor)


def sincronizar_velocidad_input():
    valor = max(1, int(st.session_state.velocidad_input))

    st.session_state.velocidad = valor
    st.session_state.velocidad_slider = valor
    st.session_state._velocidad_ui = valor

    sim.cambiar_velocidad(valor)


def sincronizar_tasa_emisión_slider():
    st.session_state.tasa_emisión_input = st.session_state.tasa_emisión_slider
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_slider)


def sincronizar_tasa_emisión_input():
    st.session_state.tasa_emisión_slider = st.session_state.tasa_emisión_input
    sim.cambiar_tasa_emisión(st.session_state.tasa_emisión_input)


def aplicar_productividad_formal(valor):
    if hasattr(sim, "cambiar_productividad_formal"):
        sim.cambiar_productividad_formal(valor)
    else:
        sim.config.productividad_formal = float(valor)


def aplicar_productividad_informal(valor):
    if hasattr(sim, "cambiar_productividad_informal"):
        sim.cambiar_productividad_informal(valor)
    else:
        sim.config.productividad_informal = float(valor)


def sincronizar_productividad_formal_slider():
    st.session_state.productividad_formal_input = st.session_state.productividad_formal_slider
    aplicar_productividad_formal(st.session_state.productividad_formal_slider)


def sincronizar_productividad_formal_input():
    st.session_state.productividad_formal_slider = st.session_state.productividad_formal_input
    aplicar_productividad_formal(st.session_state.productividad_formal_input)


def sincronizar_productividad_informal_slider():
    st.session_state.productividad_informal_input = st.session_state.productividad_informal_slider
    aplicar_productividad_informal(st.session_state.productividad_informal_slider)


def sincronizar_productividad_informal_input():
    st.session_state.productividad_informal_slider = st.session_state.productividad_informal_input
    aplicar_productividad_informal(st.session_state.productividad_informal_input)


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
                "Empleo formal": float(snap.empleo_formal),
                "Empleo informal": float(snap.empleo_informal),
                "Desempleo": float(snap.desempleo),
            })
    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos).set_index("Día").astype(float)
        st.session_state.historial = pd.concat([st.session_state.historial, df_nuevos])



run_every = 1 if st.session_state.auto_avance else None


def graficar_con_marca(df, columnas, titulo="", marcador_dia=None, marcador_texto=None):
    if df is None or df.empty:
        return

    chart_df = df.reset_index()
    chart_df = chart_df.rename(columns={chart_df.columns[0]: "día"})
    chart_df["día"] = pd.to_numeric(chart_df["día"], errors="coerce")
    chart_df = chart_df.dropna(subset=["día"])

    if chart_df.empty:
        return

    columnas_validas = [col for col in columnas if col in chart_df.columns]
    if not columnas_validas:
        return

    long_df = chart_df[["día"] + columnas_validas].melt(
        id_vars="día",
        value_vars=columnas_validas,
        var_name="serie",
        value_name="valor",
    )

    layers = [
        {
            "mark": {"type": "line"},
            "encoding": {
                "x": {"field": "día", "type": "quantitative", "title": "Día"},
                "y": {"field": "valor", "type": "quantitative"},
                "color": {
                    "field": "serie",
                    "type": "nominal",
                    "legend": {
                        "orient": "bottom",
                        "title": None,
                        "labelFontSize": 11,
                    },
                },
            },
        }
    ]

    if marcador_dia is not None and marcador_texto:
        dia_actual = int(getattr(sim.estado, "día", 0))
        if esta_activa(int(marcador_dia), dia_actual):
            layers.append(
                {
                    "data": {"values": [{"día": int(marcador_dia)}]},
                    "mark": {
                        "type": "rule",
                        "color": "red",
                        "strokeWidth": 2,
                        "strokeDash": [6, 4],
                    },
                    "encoding": {
                        "x": {"field": "día", "type": "quantitative"},
                    },
                }
            )
            layers.append(
                {
                    "data": {"values": [{"día": int(marcador_dia), "label": marcador_texto}]},
                    "mark": {
                        "type": "text",
                        "color": "red",
                        "fontWeight": "bold",
                        "dx": 5,
                        "dy": -10,
                    },
                    "encoding": {
                        "x": {"field": "día", "type": "quantitative"},
                        "text": {"field": "label", "type": "nominal"},
                    },
                }
            )

    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": long_df.to_dict(orient="records")},
        "layer": layers,
    }

    if titulo:
        spec["title"] = titulo

    st.vega_lite_chart(spec, use_container_width=True, height=300)


@st.fragment(run_every=run_every)
def controles_velocidad():

    velocidad = max(1, int(st.session_state.velocidad))

    if st.session_state.get("_velocidad_ui") != velocidad:
        st.session_state._velocidad_ui = velocidad
        st.session_state.velocidad_slider = velocidad
        st.session_state.velocidad_input = velocidad

    st.slider(
        "Velocidad (días por paso)",
        min_value=1,
        max_value=1000,
        key="velocidad_slider",
        on_change=sincronizar_velocidad_slider,
        disabled=st.session_state.ajuste_velocidad_automatico,
    )

    st.number_input(
        "Valor exacto",
        min_value=1,
        max_value=1000,
        step=1,
        key="velocidad_input",
        on_change=sincronizar_velocidad_input,
        disabled=st.session_state.ajuste_velocidad_automatico,
    )


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
                "Empleo formal",
                "Empleo informal",
                "Desempleo"
            ]
        ).astype(float)
        st.session_state.historial.index.name = "Día"
        st.session_state.auto_avance = False
        st.rerun()

    st.checkbox(
        "Ajuste automático de velocidad",
        key="ajuste_velocidad_automatico",
    )

    controles_velocidad()

    st.divider()

    st.number_input(
        "Día a marcar",
        min_value=0,
        max_value=1000000,
        step=1,
        key="marcador_dia",
    )
    st.caption("El marcador se muestra solo si el día elegido está a menos de 365 días del día actual.")

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
        min_value=0.00,
        max_value=1.00,
        step=0.01,
        key="informalidad_por_empresa_slider",
        on_change=sincronizar_informalidad_por_empresa_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0.00,
        max_value=1.00,
        step=0.01,
        key="informalidad_por_empresa_input",
        on_change=sincronizar_informalidad_por_empresa_input,
    )

    st.divider()

    st.slider(
        "Productividad formal",
        min_value=0.00,
        max_value=5.00,
        step=0.01,
        key="productividad_formal_slider",
        on_change=sincronizar_productividad_formal_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0.00,
        max_value=5.00,
        step=0.01,
        key="productividad_formal_input",
        on_change=sincronizar_productividad_formal_input,
    )

    st.slider(
        "Productividad informal",
        min_value=0.00,
        max_value=5.00,
        step=0.01,
        key="productividad_informal_slider",
        on_change=sincronizar_productividad_informal_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=0.00,
        max_value=5.00,
        step=0.01,
        key="productividad_informal_input",
        on_change=sincronizar_productividad_informal_input,
    )

    st.divider()

    st.slider(
        "Tasa emisión",
        min_value=-1.00,
        max_value=1.00,
        step=0.001,
        key="tasa_emisión_slider",
        on_change=sincronizar_tasa_emisión_slider,
    )

    st.number_input(
        "Valor exacto",
        min_value=-1.00,
        max_value=1.00,
        step=0.001,
        key="tasa_emisión_input",
        on_change=sincronizar_tasa_emisión_input,
    )


@st.fragment(run_every=run_every)
def panel():

    if st.session_state.auto_avance:
        t_inicio = time.perf_counter()
        
        snapshots = []
        v_actual = int(st.session_state.velocidad)
        for _ in range(v_actual):
            if sim.step():
                snapshots.append(sim.obtener_snapshot())
            else:
                st.session_state.auto_avance = False
                break
        registrar_snapshots(snapshots)
        
        t_fin = time.perf_counter()
        t_transcurrido = t_fin - t_inicio

        if st.session_state.get("ajuste_velocidad_automatico", True) and t_transcurrido > 0:
            fuera_de_rango = t_transcurrido < 0.99 or t_transcurrido > 1.01
            
            if fuera_de_rango:
                v_nueva = v_actual * (1.0 / t_transcurrido)
                
                v_nueva_entera = max(1, min(10000, int(round(v_nueva))))
                
                if v_nueva_entera != v_actual:
                    st.session_state.velocidad = v_nueva_entera
                    sim.cambiar_velocidad(v_nueva_entera)

        if not st.session_state.auto_avance:
            st.rerun()

    if st.session_state.salario_mínimo_automático:
        salario_metric_placeholder.metric("Valor actual calculado", f"{sim.config.salario_mínimo:.2f}")

    hay_datos = len(st.session_state.historial) > 0

    # ---------------------------------------------------------
    # 1. TARJETAS / MÉTRICAS SUPERIORES (PROMEDIO DEL TRAMO DE VELOCIDAD)
    # ---------------------------------------------------------
    (
        col_día, 
        col_salario, 
        col_salario_inf, 
        col_precio, 
        col_emp_formal, 
        col_emp_informal, 
        col_desempleo
    ) = st.columns(7)

    col_día.metric("Día", sim.estado.día)

    if hay_datos:
        n_dias = max(1, int(st.session_state.velocidad))
        historial_reciente = st.session_state.historial.tail(n_dias)

        val_salario = historial_reciente["Salario"].mean()
        val_salario_inf = historial_reciente["Salario informal"].mean()
        val_precio = historial_reciente["Precio"].mean()
        val_emp_formal = historial_reciente["Empleo formal"].mean()
        val_emp_informal = historial_reciente["Empleo informal"].mean()
        val_desempleo = historial_reciente["Desempleo"].mean()

        col_salario.metric("Salario medio", f"{val_salario:.2f}")
        col_salario_inf.metric("Salario informal med.", f"{val_salario_inf:.2f}")
        col_precio.metric("Precio medio", f"{val_precio:.2f}")
        col_emp_formal.metric("Empleo formal", f"{val_emp_formal * 100:.1f}%")
        col_emp_informal.metric("Empleo informal", f"{val_emp_informal * 100:.1f}%")
        col_desempleo.metric("Desempleo", f"{val_desempleo * 100:.1f}%")
    else:
        col_salario.metric("Salario medio", "—")
        col_salario_inf.metric("Salario informal med.", "—")
        col_precio.metric("Precio medio", "—")
        col_emp_formal.metric("Empleo formal", "—")
        col_emp_informal.metric("Empleo informal", "—")
        col_desempleo.metric("Desempleo", "—")

    # ---------------------------------------------------------
    # 2. LOS TRES GRÁFICOS APILADOS UNO DEBAJO DEL OTRO
    # ---------------------------------------------------------
    if hay_datos:
        último_día = st.session_state.historial.index.max()
        historial_filtrado = st.session_state.historial[
            st.session_state.historial.index > (último_día - 365)
        ].astype(float)

        valores_marcado = obtener_valores_marcado(sim, st.session_state)
        texto_marcado = construir_texto_marcado(valores_marcado)

        st.subheader("1. Evolución de Salarios")
        graficar_con_marca(
            historial_filtrado[["Salario", "Salario informal"]],
            ["Salario", "Salario informal"],
            "Evolución de Salarios",
            marcador_dia=st.session_state.get("marcador_dia"),
            marcador_texto=texto_marcado,
        )

        st.subheader("2. Evolución de Tasas de Empleo y Desempleo (%)")
        df_empleo_pct = historial_filtrado[["Empleo formal", "Empleo informal", "Desempleo"]] * 100
        graficar_con_marca(
            df_empleo_pct,
            list(df_empleo_pct.columns),
            "Tasas de Empleo y Desempleo (%)",
            marcador_dia=st.session_state.get("marcador_dia"),
            marcador_texto=texto_marcado,
        )

        st.subheader("3. Evolución del Precio Medio")
        graficar_con_marca(
            historial_filtrado[["Precio"]],
            ["Precio"],
            "Evolución del Precio Medio",
            marcador_dia=st.session_state.get("marcador_dia"),
            marcador_texto=texto_marcado,
        )

    else:
        st.info("Todavía no hay datos. Iniciá la simulación o avanzá un día.")


panel()