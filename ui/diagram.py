# ui/diagram.py
import streamlit as st
from ui.utils import obtener_delta_texto

SVG_TEMPLATE = """
<svg viewBox="0 0 1000 750" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif">
  <rect width="1000" height="750" fill="#121214" rx="15" />
  <defs>
    <marker id="arrowRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#e74c3c"/>
    </marker>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#3498db"/>
    </marker>
  </defs>
  <text x="500" y="50" text-anchor="middle" font-size="26" font-weight="bold" fill="#f8f9fa">
    Diagrama de Flujo Circular de la Economía
  </text>
  <rect x="350" y="95" width="300" height="100" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="10"/>
  <text x="500" y="140" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Mercado de</text>
  <text x="500" y="165" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Bienes y Servicios</text>
  <rect x="350" y="555" width="300" height="100" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="10"/>
  <text x="500" y="600" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Mercado de</text>
  <text x="500" y="625" text-anchor="middle" font-size="18" font-weight="bold" fill="#f8f9fa">Factores de Producción</text>
  <ellipse cx="140" cy="375" rx="100" ry="70" fill="#2a2415" stroke="#eab308" stroke-width="2"/>
  <text x="140" y="382" text-anchor="middle" font-size="19" font-weight="bold" fill="#f8f9fa">Empresas</text>
  <text x="140" y="405" text-anchor="middle" font-size="14" font-weight="bold" fill="#a0a0a0">{num_empresas}</text>
  <ellipse cx="860" cy="375" rx="100" ry="70" fill="#2a2415" stroke="#eab308" stroke-width="2"/>
  <text x="860" y="382" text-anchor="middle" font-size="19" font-weight="bold" fill="#f8f9fa">Familias</text>
  <text x="860" y="405" text-anchor="middle" font-size="14" font-weight="bold" fill="#a0a0a0">{num_personas}</text>
  <path d="M 215,322 C 240,275 285,215 340,185" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="240" y="235" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Bienes y Servicios</text>
  <text x="240" y="253" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">vendidos (Q)</text>
  <text x="240" y="278" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{bys_vendidos}</text>
  <path d="M 660,185 C 715,215 760,275 785,322" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="760" y="235" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Bienes y servicios</text>
  <text x="760" y="253" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">comprados (Q)</text>
  <text x="760" y="278" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{bys_comprados}</text>
  <path d="M 785,428 C 760,475 715,535 660,565" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="760" y="505" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Trabajo y factores</text>
  <text x="760" y="523" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">ofrecidos (F)</text>
  <text x="760" y="548" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{trabajo_tierra_capital}</text>
  <path d="M 340,565 C 285,535 240,475 215,428" stroke="#e74c3c" stroke-width="3" fill="none" marker-end="url(#arrowRed)"/>
  <text x="240" y="505" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">Factores de</text>
  <text x="240" y="523" font-size="13" font-weight="bold" fill="#ff7675" text-anchor="middle">producción</text>
  <text x="240" y="548" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{factores_produccion}</text>
  <path d="M 895,305 C 930,180 780,60 580,90" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="810" y="110" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Gastos ($)</text>
  <text x="810" y="135" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{gastos}</text>
  <path d="M 420,90 C 220,60 70,180 105,305" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="190" y="110" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Ingresos ($)</text>
  <text x="190" y="135" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{ingresos_empresas}</text>
  <path d="M 105,445 C 70,570 220,690 420,660" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="190" y="635" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Salarios y</text>
  <text x="190" y="655" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">beneficios ($)</text>
  <text x="190" y="680" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{salarios_rentas}</text>
  <path d="M 580,660 C 780,690 930,570 895,445" stroke="#3498db" stroke-width="3" fill="none" marker-end="url(#arrowBlue)"/>
  <text x="810" y="635" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Ingresos</text>
  <text x="810" y="655" font-size="14" font-weight="bold" fill="#74b9ff" text-anchor="middle">Familias ($)</text>
  <text x="810" y="680" font-size="15" font-weight="bold" fill="#2ecc71" text-anchor="middle">{ingresos_familias}</text>
</svg>
"""

def renderizar_diagrama(val_bienes, val_ingresos_empresas, val_gasto_empresas, num_formales, num_informales, num_empresas, num_personas, captura=None):
    if captura is not None:
        delta_bienes = obtener_delta_texto(val_bienes, captura["Bienes Vendidos"])
        delta_ingresos_empresas = obtener_delta_texto(val_ingresos_empresas, captura["Flujo Empresas (Ing)"])
        delta_gasto_empresas = obtener_delta_texto(val_gasto_empresas, captura["Flujo Empresas (Gast)"])
        delta_num_formales = obtener_delta_texto(num_formales, captura["Trabajadores Form."])
        delta_num_informales = obtener_delta_texto(num_informales, captura["Trabajadores Inf."])

        def formato_svg_comparativo(valor_actual, delta_texto, unidad=""):
            return f"{valor_actual:.1f}{unidad} ({delta_texto})"

        if "Número Empresas" in captura:
            delta_num_empresas = obtener_delta_texto(num_empresas, captura["Número Empresas"])
            texto_num_empresas = f"{num_empresas:.0f} ({delta_num_empresas})"
        else:
            texto_num_empresas = f"{num_empresas:.0f}"

        if "Número Personas" in captura:
            delta_num_personas = obtener_delta_texto(num_personas, captura["Número Personas"])
            texto_num_personas = f"{num_personas:.0f} ({delta_num_personas})"
        else:
            texto_num_personas = f"{num_personas:.0f}"

        valores_svg_comp = {
            "num_empresas": texto_num_empresas,
            "num_personas": texto_num_personas,
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

        svg_renderizado = SVG_TEMPLATE.format(**valores_svg_comp)
        svg_renderizado = (
            svg_renderizado
            .replace('id="arrowRed"', 'id="arrowRedComp"')
            .replace('id="arrowBlue"', 'id="arrowBlueComp"')
            .replace('url(#arrowRed)', 'url(#arrowRedComp)')
            .replace('url(#arrowBlue)', 'url(#arrowBlueComp)')
        )
    else:
        valores_svg = {
            "num_empresas": f"{num_empresas:.0f}",
            "num_personas": f"{num_personas:.0f}",
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