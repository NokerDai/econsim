# ui/state.py
import streamlit as st
import pandas as pd

def inicializar_estado_ui(sim):
    if "velocidad" not in st.session_state:
        st.session_state.velocidad = max(1, int(getattr(sim.config, "velocidad_streamlit", 1)))

    if "_velocidad_ui" not in st.session_state:
        st.session_state._velocidad_ui = st.session_state.velocidad

    if "auto_avance" not in st.session_state:
        st.session_state.auto_avance = False

    if "historial" not in st.session_state:
        st.session_state.historial = pd.DataFrame(
            columns=[
                "Salario", "Salario informal", "Precio Lista", "Precio Transacción",
                "Poder Compra Formal", "Poder Compra Informal", "Empleo formal",
                "Empleo informal", "Desempleo", "Bienes Vendidos", "Empresas Ingreso",
                "Empresas Gasto"
            ]
        ).astype(float)
        st.session_state.historial.index.name = "Día"

    if "valores_guardados" not in st.session_state:
        st.session_state.valores_guardados = []

    if "indice_comparacion" not in st.session_state:
        st.session_state.indice_comparacion = 0

    if "captura_activa" not in st.session_state:
        st.session_state.captura_activa = None

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

    if "necesita_rerun_completo" not in st.session_state:
        st.session_state.necesita_rerun_completo = False