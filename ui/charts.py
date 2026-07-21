# ui/charts.py
import streamlit as st
import pandas as pd
import altair as alt
from ui.marcador import esta_activa

def obtener_marcadores_activos(sim, marcadores):
    dia_actual = int(getattr(sim.estado, "día", 0))
    return [
        m for m in marcadores
        if esta_activa(int(m.get("día", -1)), dia_actual)
    ]

def graficar_line_chart(df, columnas, sim, marcadores):
    if df is None or df.empty:
        return

    columnas_validas = [c for c in columnas if c in df.columns]
    if not columnas_validas:
        return

    df = df.copy()
    df.index.name = df.index.name or "Día"
    df = df.reset_index()

    for c in columnas_validas:
        if "Precio" in c:
            df[c] = df[c].replace(0, pd.NA)

    df[columnas_validas] = df[columnas_validas].ffill().bfill().fillna(0)
    minimo = df[columnas_validas].min().min()
    maximo = df[columnas_validas].max().max()

    escala = alt.Scale(zero=False)
    if pd.notna(minimo) and abs(maximo - minimo) < 1e-4:
        margen = max(1, abs(minimo) * 0.1)
        escala = alt.Scale(domain=[minimo - margen, maximo + margen], zero=False)

    datos = df.melt(
        id_vars="Día",
        value_vars=columnas_validas,
        var_name="Métrica",
        value_name="Valor"
    )

    grafico = alt.Chart(datos).mark_line().encode(
        x=alt.X("Día:Q", title="Día"),
        y=alt.Y("Valor:Q", scale=escala, title=None),
        color=alt.Color("Métrica:N", legend=alt.Legend(title=None, orient="top"))
    )

    m_activos = obtener_marcadores_activos(sim, marcadores)
    marcadores_filtrados = [
        m for m in m_activos
        if df["Día"].min() <= m["día"] <= df["Día"].max()
    ]

    if marcadores_filtrados:
        df_m = pd.DataFrame(marcadores_filtrados)
        reglas = alt.Chart(df_m).mark_rule(
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

        etiquetas = alt.Chart(df_m).mark_text(
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