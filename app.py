# --- app.py --- ~
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
    layout="centered",
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
    
    /* Permitir saltos de línea (\n) en los deltas de st.metric */
    div[data-testid="stMetricDelta"], 
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] span {
        white-space: pre-line !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SVG_TEMPLATE = """
<svg viewBox="0 0 1000 750" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif">
  <!-- Fondo oscuro para asegurar el contraste de la interfaz -->
  <rect width="1000" height="750" fill="#121214" rx="15" />

  <defs>
    <!-- Marcadores de flecha optimizados con colores más luminosos -->
    <marker id="arrowRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#e74c3c"/>
    </marker>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#3498db"/>
    </marker>
  </defs>

  <!-- Título principal -->
  <text x="500" y="50" text-anchor="middle" font-size="26" font-weight="bold" fill="#f8f9fa">
    Diagrama de Flujo Circular de la Economía
  </text>

  <!-- Mercado de Bienes y Servicios (Superior) -->
  <rect x="350" y="95" width="300" height="100" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="10"/>
  <text x="500" y="140" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Mercado de</text>
  <text x="500" y="165" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Bienes y Servicios</text>

  <!-- Mercado de Factores de Producción (Inferior) -->
  <rect x="350" y="555" width="300" height="100" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="10"/>
  <text x="500" y="600" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Mercado de</text>
  <text x="500" y="625" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Factores de Producción</text>

  <!-- Agente: Empresas (Izquierda) -->
  <ellipse cx="140" cy="375" rx="100" ry="70" fill="#2a2415" stroke="#eab308" stroke-width="2"/>
  <text x="140" y="382" text-anchor="middle" font-size="19" font-weight="bold" fill="#f8f9fa">Empresas</text>

  <!-- Agente: Familias (Derecha) -->
  <ellipse cx="860" cy="375" rx="100" ry="70" fill="#2a2415" stroke="#eab308" stroke-width="2"/>
  <text x="860" y="382" text-anchor="middle" font-size="19" font-weight="bold" fill="#f8f9fa">Familias</text>


  <!-- ================= FLUXO REAL (Rojo/Coral - Interno) ================= -->

  <!-- Empresas -> Mercado Bienes (Bienes vendidos) -->
  <path d="M 215,322 C 240,275 285,215 340,185" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="240" y="235" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Bienes y Servicios</text>
  <text x="240" y="253" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">vendidos (Q)</text>
  <text x="240" y="278" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{bys_vendidos}</text>

  <!-- Mercado Bienes -> Familias (Bienes comprados) -->
  <path d="M 660,185 C 715,215 760,275 785,322" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="760" y="235" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Bienes y servicios</text>
  <text x="760" y="253" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">comprados (Q)</text>
  <text x="760" y="278" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{bys_comprados}</text>

  <!-- Familias -> Mercado Factores (Factores ofrecidos) -->
  <path d="M 785,428 C 760,475 715,535 660,565" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="760" y="505" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Trabajo y factores</text>
  <text x="760" y="523" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">ofrecidos (F)</text>
  <text x="760" y="548" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{trabajo_tierra_capital}</text>

  <!-- Mercado Factores -> Empresas (Factores de producción) -->
  <path d="M 340,565 C 285,535 240,475 215,428" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="240" y="505" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Factores de</text>
  <text x="240" y="523" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">producción</text>
  <text x="240" y="548" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{factores_produccion}</text>


  <!-- ================= FLUXO MONETARIO (Azul Cielo - Externo) ================= -->

  <!-- Familias -> Mercado Bienes (Gastos) -->
  <path d="M 895,305 C 930,180 780,60 580,90" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="810" y="110" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Gastos ($)</text>
  <text x="810" y="135" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{gastos}</text>

  <!-- Mercado Bienes -> Empresas (Ingresos) -->
  <path d="M 420,90 C 220,60 70,180 105,305" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="190" y="110" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Ingresos ($)</text>
  <text x="190" y="135" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{ingresos_empresas}</text>

  <!-- Empresas -> Mercado Factores (Salarios/Rentas) -->
  <path d="M 105,445 C 70,570 220,690 420,660" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="190" y="635" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Salarios y</text>
  <text x="190" y="655" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">beneficios ($)</text>
  <text x="190" y="680" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{salarios_rentas}</text>

  <!-- Mercado Factores -> Familias (Ingresos Familias) -->
  <path d="M 580,660 C 780,690 930,570 895,445" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="810" y="635" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Ingresos</text>
  <text x="810" y="655" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Familias ($)</text>
  <text x="810" y="680" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{ingresos_familias}</text>
</svg>
"""

if "simulación" not in st.session_state:
    st.session_state.simulación = Simulación(Config())

sim = st.session_state.simulación

if "velocidad" not in st.session_state:
    st.session_state.velocidad = max(
        1,
        int(getattr(sim.config, "velocidad_streamlit", 1))
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

# Inicialización de la caché para almacenar lecturas
if "valores_guardados" not in st.session_state:
    st.session_state.valores_guardados = []

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
    st.session_state.velocidad_slider = max(1, int(getattr(sim.config, "velocidad_streamlit", 1)))

if "velocidad_input" not in st.session_state:
    st.session_state.velocidad_input = max(1, int(getattr(sim.config, "velocidad_streamlit", 1)))

if "velocidad" not in st.session_state:
    st.session_state.velocidad = max(1, int(getattr(sim.config, "velocidad_streamlit", 1)))

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
    st.session_state.pestana_activa = "⚙️ Configuración"

# Bandera para coordinar recargas completas de la aplicación
if "necesita_rerun_completo" not in st.session_state:
    st.session_state.necesita_rerun_completo = False


# Sincronización inicial o reactiva del salario mínimo si está en automático
if st.session_state.get("salario_mínimo_automático", False):
    st.session_state.salario_slider = int(sim.config.salario_mínimo or 0)
    st.session_state.salario_input = int(sim.config.salario_mínimo or 0)


def sincronizar_salario_slider():
    st.session_state.salario_input = st.session_state.salario_slider
    sim.cambiar_salario_mínimo(st.session_state.salario_slider)


def sincronizar_salario_input():
    st.session_state.salario_slider = st.session_state.salario_input
    sim.cambiar_salario_mínimo(st.session_state.salario_input)


def sincronizar_salario_mínimo_automático():
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


# Callbacks simples que no ejecutan st.rerun() dentro de sí mismos
def iniciar_avance():
    st.session_state.auto_avance = True
    st.session_state.last_auto_step = time.time()
    st.session_state.pestana_activa = "📈 Gráficos de Evolución"
    st.session_state.necesita_rerun_completo = True


def detener_avance():
    st.session_state.auto_avance = False
    st.session_state.necesita_rerun_completo = True


def obtener_marcadores_activos():
    dia_actual = int(getattr(sim.estado, "día", 0))
    return [
        marcador for marcador in st.session_state.get("marcadores", [])
        if esta_activa(int(marcador.get("día", -1)), dia_actual)
    ]


def graficar_line_chart(df, columnas):
    if df is None or df.empty:
        return

    columnas = [c for c in columnas if c in df.columns]
    if not columnas:
        return

    df = df.copy()
    df.index.name = df.index.name or "Día"
    df = df.reset_index()

    for c in columnas:
        if "Precio" in c:
            df[c] = df[c].replace(0, pd.NA)

    df[columnas] = df[columnas].ffill().bfill().fillna(0)

    minimo = df[columnas].min().min()
    maximo = df[columnas].max().max()

    if pd.notna(minimo) and abs(maximo - minimo) < 1e-4:
        margen = max(1, abs(minimo) * 0.1)
        escala = alt.Scale(domain=[minimo - margen, maximo + margen], zero=False)
    else:
        escala = alt.Scale(zero=False)

    datos = df.melt(
        id_vars="Día",
        value_vars=columnas,
        var_name="Métrica",
        value_name="Valor"
    )

    grafico = alt.Chart(datos).mark_line().encode(
        x=alt.X("Día:Q", title="Día"),
        y=alt.Y("Valor:Q", scale=escala, title=None),
        color=alt.Color("Métrica:N", legend=alt.Legend(title=None, orient="top"))
    )

    marcadores = [
        m for m in obtener_marcadores_activos()
        if df["Día"].min() <= m["día"] <= df["Día"].max()
    ]

    if marcadores:
        reglas = alt.Chart(pd.DataFrame(marcadores)).mark_rule(
            color="#FF4B4B",
            strokeDash=[4, 4],
            strokeWidth=1.5
        ).encode(
            x="día:Q",
            tooltip=[
                alt.Tooltip("nombre:N", title="Parámetro"),
                alt.Tooltip("valor:Q", title="Valor"),
                alt.Tooltip("día:Q", title="Día"),
            ],
        )

        etiquetas = alt.Chart(pd.DataFrame(marcadores)).mark_text(
            align="left",
            dx=5,
            dy=12,
            color="#FF4B4B",
            fontSize=10,
            fontWeight="bold",
        ).encode(
            x="día:Q",
            y=alt.value(8),
            text="nombre:N",
        )

        grafico = alt.layer(grafico, reglas, etiquetas)

    st.altair_chart(grafico.properties(height=320).interactive(), width="stretch")


def obtener_delta_texto(actual, capturado, decimales=1):
    """
    Calcula de forma segura el incremento porcentual.
    Evita la división por cero y devuelve indicadores de infinito de manera matemáticamente correcta.
    """
    if capturado is None:
        return "N/A"
    if capturado == 0:
        if actual == 0:
            return "0.0%"
        elif actual > 0:
            return "+∞%"
        else:
            return "-∞%"
    diff_pct = ((actual - capturado) / capturado) * 100
    return f"{diff_pct:+.{decimales}f}%"


def obtener_delta_doble(actual, capturado, decimales_abs=2, decimales_rel=1):
    """
    Devuelve un texto con la variación absoluta y la relativa combinadas
    separadas por un salto de línea real (\n), habilitado mediante CSS.
    """
    if capturado is None:
        return "N/A"
    diff_abs = actual - capturado
    rel_texto = obtener_delta_texto(actual, capturado, decimales=decimales_rel)
    return f"{diff_abs:+.{decimales_abs}f}\n({rel_texto})"


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
            max_value=365,
            key="velocidad_slider",
            on_change=sincronizar_velocidad_slider,
        )

        st.number_input(
            "Valor exacto",
            min_value=1,
            max_value=365,
            step=1,
            key="velocidad_input",
            on_change=sincronizar_velocidad_input,
        )

    with col_btn_velocidad:
        if st.button("📍", key="marcar_velocidad", help="Marcar el valor actual de la velocidad en el día actual"):
            marcar_valor("Velocidad", st.session_state.velocidad)


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

        # Se muestran en formato de tasa decimal (:.4f) en lugar de porcentaje
        fila3[0].metric("Poder compra formal", f"{val_poder_f:.4f}")
        fila3[1].metric("Poder compra informal", f"{val_poder_i:.4f}")
        fila3[2].metric("Empleo formal", f"{val_emp_formal:.4f}")
        fila3[3].metric("Empleo informal", f"{val_emp_informal:.4f}")
        fila3[4].metric("Desempleo", f"{val_desempleo:.4f}")
    else:
        fila1[0].metric("Día", "—")
        fila2[0].metric("Salario mínimo", "—")

    tab_graficos, tab_flujo, tab_comparacion, tab_config = st.tabs(
        ["📈 Gráficos de Evolución", "🔄 Flujo Circular de la Economía", "⚖️ Comparación con Captura", "⚙️ Configuración"],
        key="pestana_activa",
        on_change="rerun"
    )

    # Lógica de detección de pausa si se ingresa de forma manual a la pestaña Configuración
    if st.session_state.pestana_activa == "⚙️ Configuración" and st.session_state.auto_avance:
        st.session_state.auto_avance = False
        st.session_state.necesita_rerun_completo = True

    # Comprobación de recarga completa delegada al cuerpo del fragmento
    if st.session_state.get("necesita_rerun_completo", False):
        st.session_state.necesita_rerun_completo = False
        st.rerun()

    # PESTAÑA 1: Gráficos de evolución temporal
    with tab_graficos:
        if hay_datos:
            historial_graficos = st.session_state.historial.tail(365)

            st.subheader("1. Evolución de Salarios")
            graficar_line_chart(historial_graficos, ["Salario", "Salario informal"])

            # Grafica tasas en escala decimal natural directamente
            st.subheader("2. Evolución de Tasas de Empleo y Desempleo (Tasa)")
            graficar_line_chart(historial_graficos, ["Empleo formal", "Empleo informal", "Desempleo"])

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
        else:
            st.info("Todavía no hay datos. Dirígete a la pestaña ⚙️ Configuración para iniciar la simulación.")

    # PESTAÑA 2: Diagrama de flujo circular dinámico
    with tab_flujo:
        if hay_datos:
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
            st.info("Todavía no hay datos. Dirígete a la pestaña ⚙️ Configuración para iniciar la simulación.")

    # PESTAÑA 3: Comparación con Captura
    with tab_comparacion:
        if hay_datos:
            st.subheader("Análisis de Variación con Captura de Caché")
            if not st.session_state.valores_guardados:
                st.info(
                    "No se encontraron capturas guardadas en caché. "
                    "Por favor, use el botón '💾 Guardar en Caché' en la pestaña ⚙️ Configuración "
                    "en el escenario o día que desee registrar primero."
                )
            else:
                # Construir las opciones del selector
                opciones = [
                    f"Día {cap['Día']} - (Registrado a las {cap['Hora']})" 
                    for cap in st.session_state.valores_guardados
                ]
                seleccion = st.selectbox(
                    "Seleccione la captura de referencia para comparar:", 
                    opciones
                )
                
                idx_seleccionado = opciones.index(seleccion)
                captura = st.session_state.valores_guardados[idx_seleccionado]
                
                # Fila 1: Mostrar variaciones de salarios y precios tanto en formato absoluto como relativo
                delta_sal_min = obtener_delta_doble(sim.config.salario_mínimo, captura["Salario Mínimo"])
                delta_sal_med = obtener_delta_doble(val_salario, captura["Salario Medio"])
                delta_sal_inf = obtener_delta_doble(val_salario_inf, captura["Salario Informal"])
                delta_prec_list = obtener_delta_doble(val_precio_lista, captura["Precio Lista"])
                delta_prec_trans = obtener_delta_doble(val_precio, captura["Precio Transac."])
                
                # Fila 2: Variaciones estrictamente absolutas en escala decimal
                delta_poder_f_abs = f"{(val_poder_f - captura['Poder Compra Form.']):+.4f}"
                delta_poder_i_abs = f"{(val_poder_i - captura['Poder Compra Inf.']):+.4f}"
                delta_emp_formal_abs = f"{(val_emp_formal - captura['Emp. Formal']):+.4f}"
                delta_emp_informal_abs = f"{(val_emp_informal - captura['Emp. Informal']):+.4f}"
                delta_desempleo_abs = f"{(val_desempleo - captura['Desempleo']):+.4f}"
                
                # Variaciones generales
                delta_bienes = obtener_delta_texto(val_bienes, captura["Bienes Vendidos"])
                delta_ingresos_empresas = obtener_delta_texto(val_ingresos_empresas, captura["Flujo Empresas (Ing)"])
                delta_gasto_empresas = obtener_delta_texto(val_gasto_empresas, captura["Flujo Empresas (Gast)"])

                total_trabajadores = sim.config.num_trabajadores
                num_formales = val_emp_formal * total_trabajadores
                num_informales = val_emp_informal * total_trabajadores
                delta_num_formales = obtener_delta_texto(num_formales, captura["Trabajadores Form."])
                delta_num_informales = obtener_delta_texto(num_informales, captura["Trabajadores Inf."])

                # Renderizar las tarjetas de comparación (los deltas de la Fila 1 tendrán dos líneas gracias al CSS)
                st.markdown("#### Métricas actuales y variación respecto a la captura")
                col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
                col_c1.metric("Salario Mínimo", f"{sim.config.salario_mínimo:.2f}", delta_sal_min)
                col_c2.metric("Salario Medio", f"{val_salario:.2f}", delta_sal_med)
                col_c3.metric("Salario Informal Med.", f"{val_salario_inf:.2f}", delta_sal_inf)
                col_c4.metric("Precio Lista Med.", f"{val_precio_lista:.2f}", delta_prec_list)
                col_c5.metric("Precio Transac. Med.", f"{val_precio:.2f}", delta_prec_trans)

                col_c2_1, col_c2_2, col_c2_3, col_c2_4, col_c2_5 = st.columns(5)
                col_c2_1.metric("Poder Compra Formal", f"{val_poder_f:.4f}", delta_poder_f_abs)
                col_c2_2.metric("Poder Compra Informal", f"{val_poder_i:.4f}", delta_poder_i_abs)
                col_c2_3.metric("Empleo Formal", f"{val_emp_formal:.4f}", delta_emp_formal_abs)
                col_c2_4.metric("Empleo Informal", f"{val_emp_informal:.4f}", delta_emp_informal_abs)
                col_c2_5.metric("Desempleo", f"{val_desempleo:.4f}", delta_desempleo_abs)

                st.write("---")

                # Formateador de textos para inyectar los deltas formateados en el SVG
                def formato_svg_comparativo(valor_actual, delta_texto, unidad=""):
                    return f"{valor_actual:.1f}{unidad} ({delta_texto})"

                valores_svg_comp = {
                    "bys_vendidos": formato_svg_comparativo(val_bienes, delta_bienes, " u."),
                    "bys_comprados": formato_svg_comparativo(val_bienes, delta_bienes, " u."),
                    "ingresos_empresas": formato_svg_comparativo(val_ingresos_empresas, delta_ingresos_empresas, " $"),
                    "gastos": formato_svg_comparativo(val_ingresos_empresas, delta_ingresos_empresas, " $"),
                    "factores_produccion": (
                        f"F: {num_formales:.0f} ({delta_num_formales}) | "
                        f"I: {num_informales:.0f} ({delta_num_informales})"
                    ),
                    "trabajo_tierra_capital": (
                        f"F: {num_formales:.0f} ({delta_num_formales}) | "
                        f"I: {num_informales:.0f} ({delta_num_informales})"
                    ),
                    "salarios_rentas": formato_svg_comparativo(val_gasto_empresas, delta_gasto_empresas, " $"),
                    "ingresos_familias": formato_svg_comparativo(val_gasto_empresas, delta_gasto_empresas, " $"),
                }

                # Renderizar gráfico SVG comparativo con aislamiento de marcadores para prevenir conflictos del DOM
                st.markdown("#### Diagrama Comparativo del Flujo Circular")
                svg_renderizado_comp = SVG_TEMPLATE.format(**valores_svg_comp)
                
                # Reemplazo de identificadores para que las puntas de flecha se dibujen correctamente
                svg_renderizado_comp = (
                    svg_renderizado_comp
                    .replace('id="arrowRed"', 'id="arrowRedComp"')
                    .replace('id="arrowBlue"', 'id="arrowBlueComp"')
                    .replace('url(#arrowRed)', 'url(#arrowRedComp)')
                    .replace('url(#arrowBlue)', 'url(#arrowBlueComp)')
                )
                
                svg_html_comp = f'<div style="text-align: center;">{svg_renderizado_comp}</div>'
                st.markdown(svg_html_comp, unsafe_allow_html=True)
        else:
            st.info("Todavía no hay datos. Dirígete a la pestaña ⚙️ Configuración para iniciar la simulación.")

    # PESTAÑA 4: Configuración
    with tab_config:
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

        if st.button("🔄 Reiniciar", width="stretch"):
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
            st.session_state.valores_guardados = []
            st.session_state.necesita_rerun_completo = True

        # BOTÓN PARA GUARDAR VALORES EN CACHÉ (GUARDADO COMO FLOATS)
        if st.button(
            "💾 Guardar en Caché", 
            width="stretch", 
            disabled=not hay_datos, 
            help="Guarda las métricas actuales del panel y del flujo circular en una tabla de caché"
        ):
            n_dias = max(1, int(st.session_state.velocidad))
            historial_reciente = st.session_state.historial.tail(n_dias)

            val_salario_c = historial_reciente["Salario"].mean()
            val_salario_inf_c = historial_reciente["Salario informal"].mean()
            val_precio_lista_c = historial_reciente["Precio Lista"].mean()
            val_precio_c = historial_reciente["Precio Transacción"].mean()
            val_emp_formal_c = historial_reciente["Empleo formal"].mean()
            val_emp_informal_c = historial_reciente["Empleo informal"].mean()
            val_desempleo_c = historial_reciente["Desempleo"].mean()
            val_poder_f_c = historial_reciente["Poder Compra Formal"].mean()
            val_poder_i_c = historial_reciente["Poder Compra Informal"].mean()
            val_bienes_c = historial_reciente["Bienes Vendidos"].mean()
            val_ingresos_empresas_c = historial_reciente["Empresas Ingreso"].mean()
            val_gasto_empresas_c = historial_reciente["Empresas Gasto"].mean()

            total_trabajadores = sim.config.num_trabajadores
            num_formales = val_emp_formal_c * total_trabajadores
            num_informales = val_emp_informal_c * total_trabajadores

            nueva_captura = {
                "Día": int(sim.estado.día),
                "Salario Mínimo": float(sim.config.salario_mínimo),
                "Salario Medio": float(val_salario_c),
                "Salario Informal": float(val_salario_inf_c),
                "Precio Lista": float(val_precio_lista_c),
                "Precio Transac.": float(val_precio_c),
                "Poder Compra Form.": float(val_poder_f_c),
                "Poder Compra Inf.": float(val_poder_i_c),
                "Emp. Formal": float(val_emp_formal_c),
                "Emp. Informal": float(val_emp_informal_c),
                "Desempleo": float(val_desempleo_c),
                "Bienes Vendidos": float(val_bienes_c),
                "Flujo Empresas (Ing)": float(val_ingresos_empresas_c),
                "Flujo Empresas (Gast)": float(val_gasto_empresas_c),
                "Trabajadores Form.": int(num_formales),
                "Trabajadores Inf.": int(num_informales),
                "Hora": time.strftime("%H:%M:%S")
            }
            st.session_state.valores_guardados.append(nueva_captura)
            st.toast("Captura de métricas guardada en la caché de sesión", icon="💾")

        # MOSTRAR LECTURAS EN CACHÉ SI EXISTEN (CON FORMATO SÓLO DE VISUALIZACIÓN)
        if st.session_state.valores_guardados:
            with st.expander("📂 Capturas en Caché", expanded=False):
                df_cache_visual = pd.DataFrame(st.session_state.valores_guardados).copy()
                tasa_cols = ["Emp. Formal", "Emp. Informal", "Desempleo"]
                for col in tasa_cols:
                    if col in df_cache_visual.columns:
                        df_cache_visual[col] = df_cache_visual[col].map(lambda x: f"{x:.4f}")
                float_cols = [
                    "Salario Mínimo", "Salario Medio", "Salario Informal", "Precio Lista", 
                    "Precio Transac.", "Poder Compra Form.", "Poder Compra Inf.", "Bienes Vendidos", 
                    "Flujo Empresas (Ing)", "Flujo Empresas (Gast)"
                ]
                for col in float_cols:
                    if col in df_cache_visual.columns:
                        df_cache_visual[col] = df_cache_visual[col].map(lambda x: f"{x:.2f}")

                st.dataframe(df_cache_visual, width='stretch')
                if st.button("🗑️ Limpiar Caché", key="btn_limpiar_cache", width="stretch"):
                    st.session_state.valores_guardados = []

        controles_velocidad()

        st.divider()

        st.checkbox(
            "Salario mínimo automático",
            key="salario_mínimo_automático",
            on_change=sincronizar_salario_mínimo_automático,
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

        if st.session_state.salario_mínimo_automático:
            col_tasa, col_btn_tasa = st.columns([5, 1])
            with col_tasa:
                st.slider(
                    "Tasa de salario mínimo",
                    min_value=0.0,
                    max_value=2.0,
                    step=0.01,
                    key="tasa_slider",
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


def ejecutar_aplicacion():
    # Determinar el intervalo de refresco de forma dinámica en cada ejecución del script
    if st.session_state.auto_avance:
        pestana_actual = st.session_state.get("pestana_activa", "⚙️ Configuración")
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

    auto_avance_fragment()


ejecutar_aplicacion()