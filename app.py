# --- app.py ---
import streamlit as st
import pandas as pd
import time

from config import Config
from simulation import Simulación
from ui.marcador import construir_texto_marcado
from versiones import VERSIONES_DISPONIBLES

from ui import (
    inyectar_estilos,
    obtener_delta_doble,
    graficar_line_chart,
    obtener_marcadores_activos,
    renderizar_diagrama,
    inicializar_estado_ui,
    callbacks as cb
)

st.set_page_config(
    page_icon="📈",
    page_title="econsim",
)

inyectar_estilos()

# --- PANTALLA DE SELECCIÓN INICIAL (BLOQUEANTE) ---
if "version_seleccionada" not in st.session_state:
    st.subheader("Selección de Versión del Modelo Económico")
    st.write(
        "Por favor, seleccione la versión del modelo antes de continuar. "
        "Una vez iniciada la simulación, esta configuración no podrá modificarse en caliente."
    )
    
    version_elegida = st.selectbox(
        "Versión disponible del Modelo",
        options=VERSIONES_DISPONIBLES,
        key="temp_version_selector"
    )
    
    if st.button("Confirmar Selección y Cargar Simulación", use_container_width=True):
        st.session_state.version_seleccionada = version_elegida
        # Se inicializa de inmediato la simulación con la versión seleccionada
        config = Config(version_modelo=version_elegida)
        st.session_state.simulación = Simulación(config)
        # Se preparan las variables del estado de la UI
        inicializar_estado_ui(st.session_state.simulación)
        st.rerun()
        
    st.stop() # Evita renderizar el resto del panel hasta que se presione el botón

# --- INICIALIZACIÓN COMPLEMENTARIA ---
if "simulación" not in st.session_state:
    config = Config(version_modelo=st.session_state.version_seleccionada)
    st.session_state.simulación = Simulación(config)

sim = st.session_state.simulación

# Asegurar el estado de UI
inicializar_estado_ui(sim)

# Sincronización del salario automático
if st.session_state.get("salario_mínimo_automático", False):
    val_sal = int(sim.config.salario_mínimo or 0)
    st.session_state.salario_slider = val_sal
    st.session_state.salario_input = val_sal
    st.session_state._salario_slider = val_sal
    st.session_state._salario_input = val_sal


def registrar_snapshots(snapshots):
    if not snapshots:
        return
    nuevos_datos = []
    for snap in snapshots:
        if snap.día not in st.session_state.historial.index:
            salario_f = float(snap.salario_medio)
            salario_i = float(snap.salario_informal_medio)
            precio_transaccion = float(snap.precio_transaccion_medio)

            poder_f = salario_f / precio_transaccion if precio_transaccion > 0 else 0.0
            poder_i = salario_i / precio_transaccion if precio_transaccion > 0 else 0.0

            nuevos_datos.append({
                "Día": int(snap.día),
                "Salario": salario_f,
                "Salario informal": salario_i,
                "Precio Lista": float(snap.precio_lista_medio),
                "Precio Transacción": precio_transaccion,
                "Poder Compra Formal": poder_f,
                "Poder Compra Informal": poder_i,
                "Empleo formal": float(snap.empleo_formal),
                "Empleo informal": float(snap.empleo_informal),
                "Desempleo": float(snap.desempleo),
                "Bienes Vendidos": float(snap.bienes_vendidos),
                "Calidad Media Transacción": float(snap.calidad_media),
                "Satisfacción Media": float(snap.satisfacción_media),
                "Empresas Ingreso": float(snap.empresas_ingreso),
                "Empresas Gasto": float(snap.empresas_gasto),
            })
    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos).set_index("Día").astype(float)
        st.session_state.historial = pd.concat([st.session_state.historial, df_nuevos])
        if len(st.session_state.historial) > 1000:
            st.session_state.historial = st.session_state.historial.tail(1000)


def marcar_valor(nombre, valor, día=None):
    if nombre is None:
        return
    día = int(día if día is not None else getattr(sim.estado, "día", 0))
    etiqueta = construir_texto_marcado({nombre: valor})
    marcadores = [
        m for m in st.session_state.get("marcadores", [])
        if m.get("nombre") != nombre
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
    st.session_state.pestana_activa = "📈 Gráficos de Evolución"
    st.session_state.necesita_rerun_completo = True


def detener_avance():
    st.session_state.auto_avance = False
    st.session_state.necesita_rerun_completo = True


def controles_velocidad():
    velocidad = max(1, int(st.session_state.velocidad))
    if st.session_state.get("_velocidad_ui") != velocidad:
        st.session_state._velocidad_ui = velocidad
        st.session_state.velocidad_slider = velocidad
        st.session_state.velocidad_input = velocidad
        st.session_state._velocidad_slider = velocidad
        st.session_state._velocidad_input = velocidad

    col_velocidad, col_btn = st.columns([5, 1])
    with col_velocidad:
        st.slider(
            "Velocidad (días por paso)",
            min_value=1,
            max_value=1000,
            key="_velocidad_slider",
            on_change=lambda: cb.sincronizar_velocidad_slider(sim),
        )
        st.number_input(
            "Valor exacto",
            min_value=1,
            max_value=1000,
            step=1,
            key="_velocidad_input",
            on_change=lambda: cb.sincronizar_velocidad_input(sim),
        )
    with col_btn:
        if st.button("📍", key="marcar_velocidad"):
            marcar_valor("Velocidad", st.session_state.velocidad)


def panel():
    inicializar_estado_ui(sim)
    
    hay_datos = len(st.session_state.historial) > 0
    captura = st.session_state.get("captura_activa")

    fila1 = st.columns(5)
    fila2 = st.columns(5)
    fila3 = st.columns(5)

    if hay_datos:
        historial_reciente = st.session_state.historial.tail(1)
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
        val_calidad = historial_reciente["Calidad Media Transacción"].mean()
        val_satisfaccion = historial_reciente["Satisfacción Media"].mean()
        val_ingresos_empresas = historial_reciente["Empresas Ingreso"].mean()
        val_gasto_empresas = historial_reciente["Empresas Gasto"].mean()

        delta_dia = f"{sim.estado.día - captura['Día']:+d} d." if (captura is not None and sim.estado.día != captura['Día']) else None
        fila1[0].metric("Día", sim.estado.día, delta=delta_dia)

        if captura is not None:
            fila1[4].metric("Calidad media", f"{val_calidad:.2f}", obtener_delta_doble(val_calidad, captura["Calidad Media Transacción"]))
            fila1[3].metric("Satisfacción media", f"{val_satisfaccion:.2f}", obtener_delta_doble(val_satisfaccion, captura["Satisfacción Media"]))

            fila2[0].metric("Salario mínimo", f"{sim.config.salario_mínimo:.2f}", obtener_delta_doble(sim.config.salario_mínimo, captura["Salario Mínimo"]))
            fila2[1].metric("Salario medio", f"{val_salario:.2f}", obtener_delta_doble(val_salario, captura["Salario Medio"]))
            fila2[2].metric("Salario informal med.", f"{val_salario_inf:.2f}", obtener_delta_doble(val_salario_inf, captura["Salario Informal"]))
            fila2[3].metric("Precio lista med.", f"{val_precio_lista:.2f}", obtener_delta_doble(val_precio_lista, captura["Precio Lista"]))
            fila2[4].metric("Precio transac. med.", f"{val_precio:.2f}", obtener_delta_doble(val_precio, captura["Precio Transac."]))

            fila3[0].metric("Poder compra formal", f"{val_poder_f:.4f}", f"{(val_poder_f - captura['Poder Compra Form.']):+.4f}")
            fila3[1].metric("Poder compra informal", f"{val_poder_i:.4f}", f"{(val_poder_i - captura['Poder Compra Inf.']):+.4f}")
            fila3[2].metric("Empleo formal", f"{val_emp_formal:.4f}", f"{(val_emp_formal - captura['Emp. Formal']):+.4f}")
            fila3[3].metric("Empleo informal", f"{val_emp_informal:.4f}", f"{(val_emp_informal - captura['Emp. Informal']):+.4f}")
            fila3[4].metric("Desempleo", f"{val_desempleo:.4f}", f"{(val_desempleo - captura['Desempleo']):+.4f}")
        else:
            fila1[4].metric("Calidad media", f"{val_calidad:.2f}")
            fila1[3].metric("Satisfacción media", f"{val_satisfaccion:.2f}")
            
            fila2[0].metric("Salario mínimo", f"{sim.config.salario_mínimo:.2f}")
            fila2[1].metric("Salario medio", f"{val_salario:.2f}")
            fila2[2].metric("Salario informal med.", f"{val_salario_inf:.2f}")
            fila2[3].metric("Precio lista med.", f"{val_precio_lista:.2f}")
            fila2[4].metric("Precio transac. med.", f"{val_precio:.2f}")

            fila3[0].metric("Poder compra formal", f"{val_poder_f:.4f}")
            fila3[1].metric("Poder compra informal", f"{val_poder_i:.4f}")
            fila3[2].metric("Empleo formal", f"{val_emp_formal:.4f}")
            fila3[3].metric("Empleo informal", f"{val_emp_informal:.4f}")
            fila3[4].metric("Desempleo", f"{val_desempleo:.4f}")
    else:
        fila1[0].metric("Día", "—")
        fila2[0].metric("Salario mínimo", "—")

    tab_graficos, tab_flujo, tab_config = st.tabs(
        ["📈 Gráficos de Evolución", "🔄 Flujo Circular de la Economía", "⚙️ Configuración"],
        key="pestana_activa",
        on_change="rerun"
    )

    if st.session_state.pestana_activa == "⚙️ Configuración" and st.session_state.auto_avance:
        st.session_state.auto_avance = False
        st.session_state.necesita_rerun_completo = True

    if st.session_state.get("necesita_rerun_completo", False):
        st.session_state.necesita_rerun_completo = False
        st.rerun()

    with tab_graficos:
        if hay_datos:
            historial_graficos = st.session_state.historial.tail(1000)
            st.subheader("1. Evolución de Salarios")
            graficar_line_chart(historial_graficos, ["Salario", "Salario informal"], sim, st.session_state.marcadores)

            st.subheader("2. Evolución de Tasas de Empleo y Desempleo")
            graficar_line_chart(historial_graficos, ["Empleo formal", "Empleo informal", "Desempleo"], sim, st.session_state.marcadores)

            st.subheader("3. Evolución del Poder de Compra")
            graficar_line_chart(historial_graficos, ["Poder Compra Formal", "Poder Compra Informal"], sim, st.session_state.marcadores)

            st.subheader("4. Evolución de los Precios")
            graficar_line_chart(historial_graficos, ["Precio Lista", "Precio Transacción"], sim, st.session_state.marcadores)

            marcadores_activos = obtener_marcadores_activos(sim, st.session_state.marcadores)
            if marcadores_activos:
                st.write("---")
                with st.expander("📍 Ajustes de Parámetros Activos", expanded=True):
                    for m in marcadores_activos:
                        st.markdown(f"**Día {m['día']}:** {m['label']}")
        else:
            st.info("Inicie la simulación en la pestaña Configuración.")

    with tab_flujo:
        if hay_datos:
            total_trabajadores = len(sim.estado.trabajadores)
            num_formales = val_emp_formal * total_trabajadores
            num_informales = val_emp_informal * total_trabajadores

            renderizar_diagrama(
                val_bienes, val_ingresos_empresas, val_gasto_empresas, 
                num_formales, num_informales, captura
            )
        else:
            st.info("Inicie la simulación en la pestaña Configuración.")

    with tab_config:
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
            st.session_state.clear()
            st.rerun()

        if st.button("💾 Guardar en Caché", width="stretch", disabled=not hay_datos):
            n_dias = max(1, int(st.session_state.velocidad))
            hr = st.session_state.historial.tail(n_dias)
            total_trabajadores = len(sim.estado.trabajadores)
            num_formales_c = hr["Empleo formal"].mean() * total_trabajadores
            num_informales_c = hr["Empleo informal"].mean() * total_trabajadores

            nueva_captura = {
                "Día": int(sim.estado.día),
                "Salario Mínimo": float(sim.config.salario_mínimo),
                "Salario Medio": float(hr["Salario"].mean()),
                "Salario Informal": float(hr["Salario informal"].mean()),
                "Precio Lista": float(hr["Precio Lista"].mean()),
                "Precio Transac.": float(hr["Precio Transacción"].mean()),
                "Poder Compra Form.": float(hr["Poder Compra Formal"].mean()),
                "Poder Compra Inf.": float(hr["Poder Compra Informal"].mean()),
                "Emp. Formal": float(hr["Empleo formal"].mean()),
                "Emp. Informal": float(hr["Empleo informal"].mean()),
                "Desempleo": float(hr["Desempleo"].mean()),
                "Bienes Vendidos": float(hr["Bienes Vendidos"].mean()),
                "Calidad Media Transacción": float(hr["Calidad Media Transacción"].mean()),
                "Satisfacción Media": float(hr["Satisfacción Media"].mean()),
                "Flujo Empresas (Ing)": float(hr["Empresas Ingreso"].mean()),
                "Flujo Empresas (Gast)": float(hr["Empresas Gasto"].mean()),
                "Trabajadores Form.": int(num_formales_c),
                "Trabajadores Inf.": int(num_informales_c),
                "Hora": time.strftime("%H:%M:%S")
            }
            st.session_state.valores_guardados.append(nueva_captura)
            st.session_state.indice_comparacion = len(st.session_state.valores_guardados)
            st.session_state.captura_activa = nueva_captura
            st.toast("Captura guardada en caché", icon="💾")
            st.rerun()

        if st.session_state.valores_guardados:
            opciones_comp = ["Ninguna"] + [f"Día {cap['Día']}" for cap in st.session_state.valores_guardados]
            seleccion = st.selectbox(
                "Comparar con captura:", opciones_comp,
                index=st.session_state.indice_comparacion,
                key="selector_comparacion_ui"
            )
            st.session_state.indice_comparacion = opciones_comp.index(seleccion)
            st.session_state.captura_activa = (
                st.session_state.valores_guardados[st.session_state.indice_comparacion - 1]
                if seleccion != "Ninguna" else None
            )

            if st.button("🗑️ Limpiar Caché", width="stretch"):
                st.session_state.valores_guardados = []
                st.session_state.indice_comparacion = 0
                st.session_state.captura_activa = None
                st.rerun()

        controles_velocidad()
        st.divider()

        st.checkbox(
            "Salario mínimo automático",
            key="_salario_mínimo_automático",
            on_change=lambda: cb.sincronizar_salario_mínimo_automático(sim),
        )

        if st.session_state.salario_mínimo_automático:
            col_tasa, col_btn_tasa = st.columns([5, 1])
            with col_tasa:
                st.slider(
                    "Tasa de salario mínimo", min_value=0.0, max_value=2.0, step=0.01,
                    key="_tasa_slider", on_change=lambda: cb.sincronizar_tasa(sim)
                )
            with col_btn_tasa:
                if st.button("📍", key="marcar_tasa_salario"):
                    marcar_valor("Tasa de salario mínimo", st.session_state.tasa_slider)

            col_formalidad, col_btn_formalidad = st.columns([5, 1])
            with col_formalidad:
                st.slider(
                    "Formalidad límite", min_value=0.0, max_value=1.0, step=0.01,
                    key="_formalidad_límite_slider", on_change=lambda: cb.sincronizar_formalidad_límite(sim)
                )
            with col_btn_formalidad:
                if st.button("📍", key="marcar_formalidad_límite"):
                    marcar_valor("Formalidad límite", st.session_state.formalidad_límite_slider)
            
        else:
            col_salario, col_btn_salario = st.columns([5, 1])
            with col_salario:
                st.slider(
                    "Salario mínimo", min_value=0, max_value=10000,
                    key="_salario_slider", on_change=lambda: cb.sincronizar_salario_slider(sim)
                )
                st.number_input(
                    "Valor exacto", min_value=0, max_value=10000, step=1,
                    key="_salario_input", on_change=lambda: cb.sincronizar_salario_input(sim)
                )
            with col_btn_salario:
                if st.button("📍", key="marcar_salario"):
                    marcar_valor("Salario mínimo", st.session_state.salario_slider)

        col_inf, col_btn_inf = st.columns([5, 1])
        with col_inf:
            st.slider(
                "Informalidad por empresa", min_value=0.0, max_value=1.0, step=0.01,
                key="_informalidad_por_empresa_slider", on_change=lambda: cb.sincronizar_informalidad_por_empresa_slider(sim)
            )
            st.number_input(
                "Valor exacto", min_value=0.0, max_value=1.0, step=0.01,
                key="_informalidad_por_empresa_input", on_change=lambda: cb.sincronizar_informalidad_por_empresa_input(sim)
            )
        with col_btn_inf:
            if st.button("📍", key="marcar_informalidad"):
                marcar_valor("Informalidad por empresa", st.session_state.informalidad_por_empresa_slider)

        st.divider()

        col_f, col_btn_f = st.columns([5, 1])
        with col_f:
            st.slider(
                "Productividad formal", min_value=0.0, max_value=5.0, step=0.01,
                key="_productividad_formal_slider", on_change=lambda: cb.sincronizar_productividad_formal_slider(sim)
            )
            st.number_input(
                "Valor exacto", min_value=0.0, max_value=5.0, step=0.01,
                key="_productividad_formal_input", on_change=lambda: cb.sincronizar_productividad_formal_input(sim)
            )
        with col_btn_f:
            if st.button("📍", key="marcar_productividad_formal"):
                marcar_valor("Productividad formal", st.session_state.productividad_formal_slider)

        col_i, col_btn_i = st.columns([5, 1])
        with col_i:
            st.slider(
                "Productividad informal", min_value=0.0, max_value=5.0, step=0.01,
                key="_productividad_informal_slider", on_change=lambda: cb.sincronizar_productividad_informal_slider(sim)
            )
            st.number_input(
                "Valor exacto", min_value=0.0, max_value=5.0, step=0.01,
                key="_productividad_informal_input", on_change=lambda: cb.sincronizar_productividad_informal_input(sim)
            )
        with col_btn_i:
            if st.button("📍", key="marcar_productividad_informal"):
                marcar_valor("Productividad informal", st.session_state.productividad_informal_slider)

        st.divider()

        col_sp, col_btn_sp = st.columns([5, 1])
        with col_sp:
            st.slider(
                "Sensibilidad precio", min_value=0.0, max_value=5.0, step=0.01,
                key="_sensibilidad_precio_slider", on_change=lambda: cb.sincronizar_sensibilidad_precio_slider(sim)
            )
            st.number_input(
                "Valor exacto (Sens. Precio)", min_value=0.0, max_value=5.0, step=0.01,
                key="_sensibilidad_precio_input", on_change=lambda: cb.sincronizar_sensibilidad_precio_input(sim)
            )
        with col_btn_sp:
            if st.button("📍", key="marcar_sensibilidad_precio"):
                marcar_valor("Sensibilidad precio", st.session_state.sensibilidad_precio_slider)

        st.divider()

        col_sc, col_btn_sc = st.columns([5, 1])
        with col_sc:
            st.slider(
                "Sensibilidad calidad", min_value=0.0, max_value=5.0, step=0.01,
                key="_sensibilidad_calidad_slider", on_change=lambda: cb.sincronizar_sensibilidad_calidad_slider(sim)
            )
            st.number_input(
                "Valor exacto (Sens. Calidad)", min_value=0.0, max_value=5.0, step=0.01,
                key="_sensibilidad_calidad_input", on_change=lambda: cb.sincronizar_sensibilidad_calidad_input(sim)
            )
        with col_btn_sc:
            if st.button("📍", key="marcar_sensibilidad_calidad"):
                marcar_valor("Sensibilidad calidad", st.session_state.sensibilidad_calidad_slider)

        st.divider()

        col_em, col_btn_em = st.columns([5, 1])
        with col_em:
            st.slider(
                "Tasa emisión", min_value=-1.000, max_value=1.000, step=0.001,
                key="_tasa_emisión_slider", on_change=lambda: cb.sincronizar_tasa_emisión_slider(sim)
            )
            st.number_input(
                "Valor exacto", min_value=-1.000, max_value=1.000, step=0.001,
                key="_tasa_emisión_input", on_change=lambda: cb.sincronizar_tasa_emisión_input(sim)
            )
        with col_btn_em:
            if st.button("📍", key="marcar_tasa_emision"):
                marcar_valor("Tasa emisión", st.session_state.tasa_emisión_slider)


def ejecutar_aplicacion():
    run_every_val = 1.0 if st.session_state.auto_avance else None

    @st.fragment(run_every=run_every_val)
    def auto_avance_fragment():
        if st.session_state.auto_avance:
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