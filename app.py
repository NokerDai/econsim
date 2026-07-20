# --- app.py ---
import streamlit as st
import pandas as pd
import time
import altair as alt

from config import Config
from simulation import Simulación
from salario_utils import resolver_valor_salario
from marcador import construir_texto_marcado, esta_activa


st.set_page_config(
    page_icon="📈",
    page_title="econsim",
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

SVG_TEMPLATE = """
<svg viewBox="0 0 950 700" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif">
  <defs>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#c0392b"/>
    </marker>
    <marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#2c3e50"/>
    </marker>
  </defs>

  <!-- Título -->
  <text x="475" y="40" text-anchor="middle" font-size="30" font-weight="bold" fill="#7a1f3d">
    Diagrama de Flujo Circular de la Economía
  </text>

  <!-- Mercado Bienes -->
  <rect x="330" y="80" width="290" height="130" fill="white" stroke="black" stroke-width="2"/>
  <text x="475" y="130" text-anchor="middle" font-size="18" font-weight="bold" fill="black">Mercado de</text>
  <text x="475" y="160" text-anchor="middle" font-size="18" font-weight="bold" fill="black">Bienes y Servicios</text>

  <!-- Mercado Factores -->
  <rect x="330" y="500" width="290" height="130" fill="white" stroke="black" stroke-width="2"/>
  <text x="475" y="550" text-anchor="middle" font-size="18" font-weight="bold" fill="black">Mercado de</text>
  <text x="475" y="580" text-anchor="middle" font-size="18" font-weight="bold" fill="black">Factores de</text>
  <text x="475" y="610" text-anchor="middle" font-size="18" font-weight="bold" fill="black">Producción</text>

  <!-- Empresas -->
  <ellipse cx="120" cy="360" rx="115" ry="70" fill="#f0ad1f" stroke="#333" stroke-width="1"/>
  <text x="120" y="368" text-anchor="middle" font-size="19" font-weight="bold" fill="black">Empresas</text>

  <!-- Familias -->
  <ellipse cx="830" cy="360" rx="115" ry="70" fill="#f0ad1f" stroke="#333" stroke-width="1"/>
  <text x="830" y="368" text-anchor="middle" font-size="19" font-weight="bold" fill="black">Familias</text>

  <!-- Empresas -> Mercado -->
  <path d="M150,300 L330,150" stroke="#c0392b" stroke-width="4" fill="none" marker-end="url(#arrowRed)"/>
  <text x="150" y="220" font-size="16" font-weight="bold" fill="white">Bienes y Servicios</text>
  <text x="150" y="240" font-size="16" font-weight="bold" fill="white">vendidos (Q)</text>
  <text x="150" y="262" font-size="16" fill="#1a5d1a" font-weight="bold">{bys_vendidos}</text>

  <!-- Ingresos Empresas -->
  <path d="M330,110 L90,110 L90,300" stroke="#2c3e50" stroke-width="4" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="150" y="100" font-size="20" font-weight="bold" fill="white">Ingresos ($)</text>
  <text x="90" y="200" font-size="16" fill="#1a5d1a" font-weight="bold">{ingresos_empresas}</text>

  <!-- Gastos -->
  <path d="M620,110 L860,110 L860,300" stroke="#2c3e50" stroke-width="4" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="700" y="100" font-size="20" font-weight="bold" fill="white">Gastos ($)</text>
  <text x="800" y="200" font-size="16" fill="#1a5d1a" font-weight="bold">{gastos}</text>

  <!-- Mercado -> Familias -->
  <path d="M620,150 L800,300" stroke="#c0392b" stroke-width="4" fill="none" marker-end="url(#arrowRed)"/>
  <text x="640" y="220" font-size="16" font-weight="bold" fill="white">Bienes y</text>
  <text x="640" y="240" font-size="16" font-weight="bold" fill="white">servicios comprados (Q)</text>
  <text x="640" y="262" font-size="16" fill="#1a5d1a" font-weight="bold">{bys_comprados}</text>

  <!-- Factores -> Empresas -->
  <path d="M330,570 L150,420" stroke="#c0392b" stroke-width="4" fill="none" marker-end="url(#arrowRed)"/>
  <text x="150" y="475" font-size="16" font-weight="bold" fill="white">Factores de</text>
  <text x="150" y="495" font-size="16" font-weight="bold" fill="white">producción</text>
  <text x="150" y="517" font-size="16" fill="#1a5d1a" font-weight="bold">{factores_produccion}</text>

  <!-- Empresas -> Mercado Factores -->
  <path d="M90,420 L90,610 L330,610" stroke="#2c3e50" stroke-width="4" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="100" y="650" font-size="16" font-weight="bold" fill="white">Salarios y</text>
  <text x="100" y="670" font-size="16" font-weight="bold" fill="white">beneficios ($)</text>
  <text x="100" y="500" font-size="16" fill="#1a5d1a" font-weight="bold">{salarios_rentas}</text>

  <!-- Familias -> Mercado Factores -->
  <path d="M800,420 L620,570" stroke="#c0392b" stroke-width="4" fill="none" marker-end="url(#arrowRed)"/>
  <text x="640" y="475" font-size="16" font-weight="bold" fill="white">Trabajo y</text>
  <text x="640" y="495" font-size="16" font-weight="bold" fill="white">factores ofrecidos</text>
  <text x="640" y="517" font-size="16" fill="#1a5d1a" font-weight="bold">{trabajo_tierra_capital}</text>

  <!-- Ingresos Familias -->
  <path d="M860,420 L860,610 L620,610" stroke="#2c3e50" stroke-width="4" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="700" y="650" font-size="20" font-weight="bold" fill="white">Ingresos ($)</text>
  <text x="800" y="500" font-size="16" fill="#1a5d1a" font-weight="bold">{ingresos_familias}</text>
</svg>
"""

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

if "last_auto_step" not in st.session_state:
    st.session_state.last_auto_step = time.time()

if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(
        columns=[
            "Salario",
            "Salario informal",
            "Precio Lista",
            "Precio Transacción",
            "Poder Compra Formal",
            "Poder Compra Informal",
            "Empleo formal",
            "Empleo informal",
            "Desempleo",
            "Bienes Vendidos",
            "Empresas Ingreso",
            "Empresas Gasto"
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

if "marcadores" not in st.session_state:
    st.session_state.marcadores = []

if "productividad_formal_slider" not in st.session_state:
    st.session_state.productividad_formal_slider = float(sim.config.productividad_formal)

if "productividad_formal_input" not in st.session_state:
    st.session_state.productividad_formal_input = float(sim.config.productividad_formal)

if "productividad_informal_slider" not in st.session_state:
    st.session_state.productividad_informal_slider = float(sim.config.productividad_informal)

if "productividad_informal_input" not in st.session_state:
    st.session_state.productividad_informal_input = float(sim.config.productividad_informal)


if "pestana_activa" not in st.session_state:
    st.session_state.pestana_activa = "📈 Gráficos de Evolución"


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
            salario_f = float(snap.salario_medio)
            salario_i = float(snap.salario_informal_medio)
            precio_lista = float(snap.precio_lista_medio)
            precio_transaccion = float(snap.precio_transaccion_medio)

            poder_f = salario_f / precio_transaccion if precio_transaccion > 0 else 0.0
            poder_i = salario_i / precio_transaccion if precio_transaccion > 0 else 0.0

            nuevos_datos.append({
                "Día": int(snap.día),
                "Salario": salario_f,
                "Salario informal": salario_i,
                "Precio Lista": precio_lista,
                "Precio Transacción": precio_transaccion,
                "Poder Compra Formal": poder_f,
                "Poder Compra Informal": poder_i,
                "Empleo formal": float(snap.empleo_formal),
                "Empleo informal": float(snap.empleo_informal),
                "Desempleo": float(snap.desempleo),
                "Bienes Vendidos": float(snap.bienes_vendidos),
                "Empresas Ingreso": float(snap.empresas_ingreso),
                "Empresas Gasto": float(snap.empresas_gasto),
            })
    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos).set_index("Día").astype(float)
        st.session_state.historial = pd.concat([st.session_state.historial, df_nuevos])
        
        if len(st.session_state.historial) > 400:
            st.session_state.historial = st.session_state.historial.tail(400)


def marcar_valor(nombre, valor, día=None):
    if nombre is None:
        return

    día = int(día if día is not None else getattr(sim.estado, "día", 0))
    etiqueta = construir_texto_marcado({nombre: valor})

    marcadores = [
        marcador for marcador in st.session_state.get("marcadores", [])
        if marcador.get("nombre") != nombre
    ]

    marcadores.append({
        "nombre": nombre,
        "label": etiqueta,
        "valor": valor,
        "día": día,
    })
    st.session_state.marcadores = marcadores


def iniciar_avance():
    st.session_state.auto_avance = True
    st.session_state.last_auto_step = time.time()


def detener_avance():
    st.session_state.auto_avance = False


def obtener_marcadores_activos():
    dia_actual = int(getattr(sim.estado, "día", 0))
    return [
        marcador for marcador in st.session_state.get("marcadores", [])
        if esta_activa(int(marcador.get("día", -1)), dia_actual)
    ]


def graficar_line_chart(df, columnas, titulo=""):
    if df is None or df.empty:
        return

    columnas_validas = [col for col in columnas if col in df.columns]
    if not columnas_validas:
        return

    df_reset = df.copy()
    if df_reset.index.name is None:
        df_reset.index.name = "Día"
    df_reset = df_reset.reset_index()

    for col in columnas_validas:
        if "Precio" in col:
            df_reset[col] = df_reset[col].replace(0.0, float('nan'))

    df_reset[columnas_validas] = df_reset[columnas_validas].ffill().bfill().fillna(0.0)

    if len(columnas_validas) == 1:
        col = columnas_validas[0]
        min_val = df_reset[col].min()
        max_val = df_reset[col].max()
    else:
        min_val = df_reset[columnas_validas].min().min()
        max_val = df_reset[columnas_validas].max().max()

    if pd.notna(min_val) and pd.notna(max_val) and abs(max_val - min_val) < 1e-4:
        margen = max(1.0, abs(min_val) * 0.1)
        y_scale = alt.Scale(domain=[min_val - margen, max_val + margen], zero=False)
    else:
        y_scale = alt.Scale(zero=False)

    if len(columnas_validas) == 1:
        col = columnas_validas[0]
        chart_line = alt.Chart(df_reset).mark_line().encode(
            x=alt.X("Día:Q", title="Día"),
            y=alt.Y(f"{col}:Q", title=None, scale=y_scale)
        )
    else:
        df_melted = df_reset.melt(
            id_vars=["Día"],
            value_vars=columnas_validas,
            var_name="Métrica",
            value_name="Valor"
        )
        chart_line = alt.Chart(df_melted).mark_line().encode(
            x=alt.X("Día:Q", title="Día"),
            y=alt.Y("Valor:Q", title=None, scale=y_scale),
            color=alt.Color("Métrica:N", legend=alt.Legend(orient="top", title=None))
        )

    marcadores_activos = obtener_marcadores_activos()
    min_dia = df_reset["Día"].min()
    max_dia = df_reset["Día"].max()

    marcadores_filtrados = [
        m for m in marcadores_activos
        if min_dia <= m["día"] <= max_dia
    ]

    if marcadores_filtrados:
        df_rules = pd.DataFrame(marcadores_filtrados)
        
        rules = alt.Chart(df_rules).mark_rule(
            color="#FF4B4B",
            strokeDash=[4, 4],
            strokeWidth=1.5
        ).encode(
            x="día:Q",
            tooltip=[
                alt.Tooltip("nombre:N", title="Parámetro"),
                alt.Tooltip("valor:Q", title="Valor Ajustado"),
                alt.Tooltip("día:Q", title="Día del Ajuste")
            ]
        )

        labels = alt.Chart(df_rules).mark_text(
            align="left",
            dx=5,
            dy=12,
            color="#FF4B4B",
            fontSize=10,
            fontWeight="bold"
        ).encode(
            x="día:Q",
            y=alt.value(8),
            text="nombre:N"
        )

        chart = alt.layer(chart_line, rules, labels).properties(
            height=320
        ).interactive()
    else:
        chart = chart_line.properties(
            height=320
        ).interactive()

    st.altair_chart(chart, use_container_width=True)


if st.session_state.auto_avance:
    pestana_actual = st.session_state.get("pestana_activa", "📈 Gráficos de Evolución")
    if pestana_actual == "🔄 Flujo Circular de la Economía":
        run_every_val = 1.0
    else:
        run_every_val = 1.0
else:
    run_every_val = None


@st.fragment(run_every=run_every_val)
def auto_avance_fragment():
    if st.session_state.auto_avance:
        st.session_state.last_auto_step = time.time()
        snapshots = []
        
        v_actual = max(1, int(st.session_state.velocidad))
        
        for _ in range(v_actual):
            if sim.step():
                snapshots.append(sim.obtener_snapshot())
            else:
                st.session_state.auto_avance = False
                break
        registrar_snapshots(snapshots)

    panel()


def controles_velocidad():

    velocidad = max(1, int(st.session_state.velocidad))

    if st.session_state.get("_velocidad_ui") != velocidad:
        st.session_state._velocidad_ui = velocidad
        st.session_state.velocidad_slider = velocidad
        st.session_state.velocidad_input = velocidad

    col_velocidad, col_btn_velocidad = st.columns([5, 1])
    with col_velocidad:
        st.slider(
            "Velocidad (días por paso)",
            min_value=1,
            max_value=1000,
            key="velocidad_slider",
            on_change=sincronizar_velocidad_slider,
        )

        st.number_input(
            "Valor exacto",
            min_value=1,
            max_value=1000,
            step=1,
            key="velocidad_input",
            on_change=sincronizar_velocidad_input,
        )

    with col_btn_velocidad:
        if st.button("📍", key="marcar_velocidad", help="Marcar el valor actual de la velocidad en el día actual"):
            marcar_valor("Velocidad", st.session_state.velocidad)


with st.sidebar:
    st.subheader("Control de ejecución")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.session_state.auto_avance:
            st.button("⏸ Pausar", width="stretch", on_click=detener_avance)
        else:
            st.button("▶ Iniciar", width="stretch", on_click=iniciar_avance)

    with col_btn2:
        if st.button("⏭ Día", disabled=st.session_state.auto_avance, width="stretch"):
            if sim.step():
                registrar_snapshots([sim.obtener_snapshot()])
            st.rerun()

    if st.button("🔄 Reiniciar", width="stretch"):
        detener_avance()
        sim.reset()
        st.session_state.historial = pd.DataFrame(
            columns=[
                "Salario",
                "Salario informal",
                "Precio Lista",
                "Precio Transacción",
                "Poder Compra Formal",
                "Poder Compra Informal",
                "Empleo formal",
                "Empleo informal",
                "Desempleo",
                "Bienes Vendidos",
                "Empresas Ingreso",
                "Empresas Gasto"
            ]
        ).astype(float)
        st.session_state.historial.index.name = "Día"
        st.session_state.auto_avance = False
        st.rerun()

    controles_velocidad()

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
        col_tasa, col_btn_tasa = st.columns([5, 1])
        with col_tasa:
            st.slider(
                "Tasa de salario mínimo",
                min_value=0.0,
                max_value=2.0,
                step=0.01,
                key="tasa_slider",
                value=st.session_state.tasa_slider,
                on_change=sincronizar_tasa,
            )
        with col_btn_tasa:
            if st.button("📍", key="marcar_tasa_salario", help="Marcar el valor actual de la tasa de salario mínimo en el día actual"):
                marcar_valor("Tasa de salario mínimo", st.session_state.tasa_slider)
    else:
        col_salario, col_btn_salario = st.columns([5, 1])
        with col_salario:
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
        with col_btn_salario:
            if st.button("📍", key="marcar_salario", help="Marcar el valor actual del salario mínimo en el día actual"):
                marcar_valor("Salario mínimo", st.session_state.salario_slider)


    col_informalidad, col_btn_informalidad = st.columns([5, 1])
    with col_informalidad:
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
    with col_btn_informalidad:
        if st.button("📍", key="marcar_informalidad", help="Marcar el valor actual de la informalidad por empresa"):
            marcar_valor("Informalidad por empresa", st.session_state.informalidad_por_empresa_slider)

    st.divider()

    col_formal, col_btn_formal = st.columns([5, 1])
    with col_formal:
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
    with col_btn_formal:
        if st.button("📍", key="marcar_productividad_formal", help="Marcar el valor actual de la productividad formal"):
            marcar_valor("Productividad formal", st.session_state.productividad_formal_slider)

    col_informal, col_btn_informal = st.columns([5, 1])
    with col_informal:
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
    with col_btn_informal:
        if st.button("📍", key="marcar_productividad_informal", help="Marcar el valor actual de la productividad informal"):
            marcar_valor("Productividad informal", st.session_state.productividad_informal_slider)

    st.divider()

    col_emision, col_btn_emision = st.columns([5, 1])
    with col_emision:
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
    with col_btn_emision:
        if st.button("📍", key="marcar_tasa_emision", help="Marcar el valor actual de la tasa de emisión"):
            marcar_valor("Tasa emisión", st.session_state.tasa_emisión_slider)


def panel():
    hay_datos = len(st.session_state.historial) > 0

    fila1 = st.columns(5)
    fila2 = st.columns(5)
    fila3 = st.columns(5)

    if hay_datos:
        n_dias = max(1, int(st.session_state.velocidad))
        historial_reciente = st.session_state.historial.tail(n_dias)

        val_salario = historial_reciente["Salario"].mean()
        val_salario_inf = historial_reciente["Salario informal"].mean()
        val_precio_lista = historial_reciente["Precio Lista"].mean()
        val_precio = historial_reciente["Precio Transacción"].mean()
        val_emp_formal = historial_reciente["Empleo formal"].mean()
        val_emp_informal = historial_reciente["Empleo informal"].mean()
        val_desempleo = historial_reciente["Desempleo"].mean()
        val_poder_f = historial_reciente["Poder Compra Formal"].mean()
        val_poder_i = historial_reciente["Poder Compra Informal"].mean()
        val_bienes = historial_reciente["Bienes Vendidos"].mean()
        val_ingresos_empresas = historial_reciente["Empresas Ingreso"].mean()
        val_gasto_empresas = historial_reciente["Empresas Gasto"].mean()

        fila1[0].metric("Día", sim.estado.día)

        fila2[0].metric("Salario mínimo", f"{sim.config.salario_mínimo:.2f}")
        fila2[1].metric("Salario medio", f"{val_salario:.2f}")
        fila2[2].metric("Salario informal med.", f"{val_salario_inf:.2f}")
        fila2[3].metric("Precio lista med.", f"{val_precio_lista:.2f}")
        fila2[4].metric("Precio transac. med.", f"{val_precio:.2f}")

        fila3[0].metric("Poder compra formal", f"{val_poder_f:.2f}")
        fila3[1].metric("Poder compra informal", f"{val_poder_i:.2f}")
        fila3[2].metric("Empleo formal", f"{val_emp_formal * 100:.1f}%")
        fila3[3].metric("Empleo informal", f"{val_emp_informal * 100:.1f}%")
        fila3[4].metric("Desempleo", f"{val_desempleo * 100:.1f}%")
    else:
        fila1[0].metric("Día", "—")
        fila2[0].metric("Salario mínimo", "—")

    if hay_datos:
        tab_graficos, tab_flujo = st.tabs(
            ["📈 Gráficos de Evolución", "🔄 Flujo Circular de la Economía"],
            key="pestana_activa",
            on_change="rerun"
        )

        # PESTAÑA 1: Gráficos de evolución temporal
        with tab_graficos:
            historial_graficos = st.session_state.historial.tail(365)

            st.subheader("1. Evolución de Salarios")
            graficar_line_chart(historial_graficos, ["Salario", "Salario informal"])

            st.subheader("2. Evolución de Tasas de Empleo y Desempleo (%)")
            df_empleo_pct = historial_graficos[["Empleo formal", "Empleo informal", "Desempleo"]] * 100
            graficar_line_chart(df_empleo_pct, ["Empleo formal", "Empleo informal", "Desempleo"])

            st.subheader("3. Evolución del Poder de Compra")
            graficar_line_chart(historial_graficos, ["Poder Compra Formal", "Poder Compra Informal"])

            st.subheader("4. Evolución de los Precios")
            graficar_line_chart(historial_graficos, ["Precio Lista", "Precio Transacción"])

            marcadores_activos = obtener_marcadores_activos()
            if marcadores_activos:
                st.write("---")
                with st.expander("📍 Ajustes de Parámetros Activos (Últimos 365 días)", expanded=True):
                    for marcador in marcadores_activos:
                        st.markdown(f"**Día {marcador['día']}:** {marcador['label']}")

        # PESTAÑA 2: Diagrama de flujo circular dinámico
        with tab_flujo:
            st.markdown("### Flujos de Mercado de Bienes y Factores de Producción")
            
            total_trabajadores = sim.config.num_trabajadores
            num_formales = val_emp_formal * total_trabajadores
            num_informales = val_emp_informal * total_trabajadores

            valores_svg = {
                "bys_vendidos": f"{val_bienes:.1f} u.",
                "bys_comprados": f"{val_bienes:.1f} u.",
                "ingresos_empresas": f"$ {val_ingresos_empresas:,.2f}",
                "gastos": f"$ {val_ingresos_empresas:,.2f}",
                "factores_produccion": f"F: {num_formales:.0f} | I: {num_informales:.0f}",
                "trabajo_tierra_capital": f"F: {num_formales:.0f} | I: {num_informales:.0f}",
                "salarios_rentas": f"$ {val_gasto_empresas:,.2f}",
                "ingresos_familias": f"$ {val_gasto_empresas:,.2f}",
            }

            svg_renderizado = SVG_TEMPLATE.format(**valores_svg)
            svg_html = f'<div style="text-align: center;">{svg_renderizado}</div>'
            st.markdown(svg_html, unsafe_allow_html=True)

    else:
        st.info("Todavía no hay datos. Iniciá la simulación o avanzá un día.")


auto_avance_fragment()