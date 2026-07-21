# ui/utils.py
import streamlit as st

HTML_CSS = """
<style>
div[data-testid="stNumberInput"] button {
    display: none !important;
}
div[data-testid="stNumberInput"] input {
    padding-right: 1rem !important;
}
div[data-testid="stNumberInput"] input[type=number]::-webkit-inner-spin-button, 
div[data-testid="stNumberInput"] input[type=number]::-webkit-outer-spin-button { 
    -webkit-appearance: none; 
    margin: 0; 
}
div[data-testid="stNumberInput"] input[type=number] {
    -moz-appearance: textfield;
}
div[data-testid="stMetricDelta"], 
div[data-testid="stMetricDelta"] > div,
div[data-testid="stMetricDelta"] span {
    white-space: pre-line !important;
}
</style>
"""

def inyectar_estilos():
    st.markdown(HTML_CSS, unsafe_allow_html=True)

def obtener_delta_texto(actual, capturado, decimales=1):
    if capturado is None:
        return "N/A"
    if capturado == 0:
        if actual == 0:
            return "0.0%"
        return "+∞%" if actual > 0 else "-∞%"
    diff_pct = ((actual - capturado) / capturado) * 100
    return f"{diff_pct:+.{decimales}f}%"

def obtener_delta_doble(actual, capturado, decimales_abs=2, decimales_rel=1):
    if capturado is None:
        return "N/A"
    diff_abs = actual - capturado
    rel_texto = obtener_delta_texto(actual, capturado, decimales=decimales_rel)
    return f"{diff_abs:+.{decimales_abs}f}\n({rel_texto})"