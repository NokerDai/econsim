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
        st.session_state.informalidad_por_empresa_slider = float(sim.config.informalidad_por_empresa)

    if "informalidad_por_empresa_input" not in st.session_state:
        st.session_state.informalidad_por_empresa_input = float(sim.config.informalidad_por_empresa)

    if "tasa_slider" not in st.session_state:
        st.session_state.tasa_slider = float(getattr(sim.config, "tasa_salario_mínimo", 0.3))
    
    if "formalidad_límite_slider" not in st.session_state:
        st.session_state.formalidad_límite_slider = float(getattr(sim.config, "salario_mínimo_automático_formalidad_límite", 0.0))

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

    if "sensibilidad_precio_slider" not in st.session_state:
        st.session_state.sensibilidad_precio_slider = float(sim.config.sensibilidad_precio)

    if "sensibilidad_precio_input" not in st.session_state:
        st.session_state.sensibilidad_precio_input = float(sim.config.sensibilidad_precio)

    if "sensibilidad_calidad_slider" not in st.session_state:
        st.session_state.sensibilidad_calidad_slider = float(sim.config.sensibilidad_calidad)

    if "sensibilidad_calidad_input" not in st.session_state:
        st.session_state.sensibilidad_calidad_input = float(sim.config.sensibilidad_calidad)

    if "pestana_activa" not in st.session_state:
        st.session_state.pestana_activa = "⚙️ Configuración"

    if "necesita_rerun_completo" not in st.session_state:
        st.session_state.necesita_rerun_completo = False

    st.session_state._salario_mínimo_automático = bool(st.session_state.salario_mínimo_automático)
    st.session_state._salario_slider = int(st.session_state.salario_slider)
    st.session_state._salario_input = int(st.session_state.salario_input)
    st.session_state._informalidad_por_empresa_slider = float(st.session_state.informalidad_por_empresa_slider)
    st.session_state._informalidad_por_empresa_input = float(st.session_state.informalidad_por_empresa_input)
    st.session_state._tasa_slider = float(st.session_state.tasa_slider)
    st.session_state._formalidad_límite_slider = float(st.session_state.formalidad_límite_slider)
    st.session_state._velocidad_slider = int(st.session_state.velocidad_slider)
    st.session_state._velocidad_input = int(st.session_state.velocidad_input)
    st.session_state._tasa_emisión_slider = float(st.session_state.tasa_emisión_slider)
    st.session_state._tasa_emisión_input = float(st.session_state.tasa_emisión_input)
    st.session_state._productividad_formal_slider = float(st.session_state.productividad_formal_slider)
    st.session_state._productividad_formal_input = float(st.session_state.productividad_formal_input)
    st.session_state._productividad_informal_slider = float(st.session_state.productividad_informal_slider)
    st.session_state._productividad_informal_input = float(st.session_state.productividad_informal_input)
    st.session_state._sensibilidad_precio_slider = float(st.session_state.sensibilidad_precio_slider)
    st.session_state._sensibilidad_precio_input = float(st.session_state.sensibilidad_precio_input)
    st.session_state._sensibilidad_calidad_slider = float(st.session_state.sensibilidad_calidad_slider)
    st.session_state._sensibilidad_calidad_input = float(st.session_state.sensibilidad_calidad_input)