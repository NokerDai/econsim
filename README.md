# econsim (versión Streamlit)

Misma simulación económica, con la interfaz reescrita en Streamlit en vez de PySide6.

## Qué se reutilizó tal cual (sin tocar)
`config.py`, `state.py`, `snapshot.py`, `simulation.py`, `models/`, `markets/`
(con tu fix del vencimiento de contratos), `estadisticas/`. Ninguno de estos
archivos dependía de Qt, así que el motor de la simulación es exactamente el
mismo que en la versión de escritorio.

## Qué se reescribió
Solo la interfaz: `ui/ventana.py` y `ui/grafico.py` (Qt) se reemplazan por
`app.py` (Streamlit). Los sliders/botones llaman a los mismos métodos de
`Simulación` (`step`, `reset`, `cambiar_salario_mínimo`, `cambiar_emisión`)
que ya existían.

Nota: no se usan `Simulación.iniciar()` / `ejecutar()` (el hilo en
background), porque en Streamlit el auto-avance se resuelve con
`st.fragment(run_every=...)`, que reejecuta el panel automáticamente sin
necesidad de un thread aparte.

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Controles
- **Iniciar / Pausar**: prende o apaga el auto-avance.
- **Día siguiente**: avanza un día manualmente (deshabilitado mientras corre el auto-avance).
- **Velocidad**: cuántos días avanza por cada actualización automática (~cada 0.4s).
- **Salario mínimo** / **Emisión monetaria diaria**: las mismas políticas configurables que en la versión de escritorio.
- **Reiniciar**: vuelve a crear el estado desde cero (misma semilla).

El gráfico muestra una ventana móvil de los últimos 365 días simulados,
igual que la versión de escritorio (el recorte se hace por valor de día,
no por cantidad de puntos, para que funcione bien también con "Velocidad" > 1).
