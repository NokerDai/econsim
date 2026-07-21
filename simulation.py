# simulation.py
import importlib
import threading
import time

import snapshot
import state
from estadisticas import actualizar_estadisticas

class Simulación:
    def __init__(self, config):
        self.config = config
        self.corriendo = False
        self.hilo = None
        self.callbacks = []
        self.lock = threading.Lock()

        try:
            ruta_version = f"versiones.{config.version_modelo}"
            self.modulo_version = importlib.import_module(ruta_version)
        except ModuleNotFoundError as e:
            raise ValueError(f"La versión del modelo '{config.version_modelo}' no fue encontrada.") from e

        self.estado = state.Estado(
            config, 
            self.modulo_version.Empresa, 
            self.modulo_version.Trabajador
        )

    def step(self):
        with self.lock:
            self.estado.día += 1

            # NUEVO: Llama a las funciones del módulo importado dinámicamente
            self.modulo_version.emisión_monetaria(self.estado)
             
            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            self.modulo_version.mercado_laboral(self.estado)

            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            self.modulo_version.mercado_productos(self.estado)

            actualizar_estadisticas(self.estado)

        if self.estado.día % self.config.frecuencia_actualización == 0:
            self.notificar()

        return True

    def agregar_callback(self, callback):
        self.callbacks.append(callback)

    def obtener_snapshot(self):
        with self.lock:
            estadísticas = self.estado.estadisticas
            return snapshot.Snapshot(
                día=self.estado.día,
                salario_medio=estadísticas.salario_medio[-1] if estadísticas.salario_medio else 0,
                salario_informal_medio=estadísticas.salario_informal_medio[-1] if estadísticas.salario_informal_medio else 0,
                precio_lista_medio=estadísticas.precio_lista_medio[-1] if estadísticas.precio_lista_medio else 0,
                precio_transaccion_medio=estadísticas.precio_transaccion_medio[-1] if estadísticas.precio_transaccion_medio else 0,
                empleo_formal=estadísticas.empleo_formal[-1] if estadísticas.empleo_formal else 0,
                empleo_informal=estadísticas.empleo_informal[-1] if estadísticas.empleo_informal else 0,
                desempleo=estadísticas.desempleo[-1] if estadísticas.desempleo else 0,
                tasa_emisión=self.config.tasa_emisión,
                salario_mínimo=self.config.salario_mínimo,
                salario_mínimo_automático=self.config.salario_mínimo_automático,
                informalidad_por_empresa=self.config.informalidad_por_empresa,
                bienes_vendidos=estadísticas.bienes_vendidos[-1] if estadísticas.bienes_vendidos else 0.0,
                calidad_media=estadísticas.calidad_media[-1] if estadísticas.calidad_media else 0.0,
                empresas_ingreso=estadísticas.empresas_ingreso[-1] if estadísticas.empresas_ingreso else 0.0,
                empresas_gasto=estadísticas.empresas_gasto[-1] if estadísticas.empresas_gasto else 0.0,
            )

    def notificar(self):
        snapshot_obj = self.obtener_snapshot()
        for callback in self.callbacks:
            callback(snapshot_obj)

    def ejecutar(self):
        while self.corriendo:
            self.step()
            time.sleep(self.config.velocidad)

    def iniciar(self):
        if self.corriendo:
            return
        self.corriendo = True
        self.hilo = threading.Thread(target=self.ejecutar, daemon=True)
        self.hilo.start()

    def pausar(self):
        self.corriendo = False

    def continuar(self):
        self.iniciar()

    def reset(self):
        with self.lock:
            self.corriendo = False
            self.estado = state.Estado(self.config, self.modulo_version.Empresa, self.modulo_version.Trabajador)
        self.notificar()

    def cambiar_tasa_emisión(self, valor):
        with self.lock:
            self.config.tasa_emisión = valor

    def cambiar_salario_mínimo(self, valor):
        with self.lock:
            self.config.salario_mínimo = valor

    def cambiar_informalidad_por_empresa(self, valor):
        with self.lock:
            self.config.informalidad_por_empresa = valor

    def cambiar_productividad_formal(self, valor):
        with self.lock:
            self.config.productividad_formal = float(valor)

    def cambiar_productividad_informal(self, valor):
        with self.lock:
            self.config.productividad_informal = float(valor)

    def cambiar_velocidad(self, valor):
        with self.lock:
            self.config.velocidad = valor
            self.config.velocidad_streamlit = valor

    def cambiar_sensibilidad_precio(self, valor):
        with self.lock:
            self.config.sensibilidad_precio = float(valor)

    def cambiar_sensibilidad_calidad(self, valor):
        with self.lock:
            self.config.sensibilidad_calidad = float(valor)

    def obtener_parametros(self):
        with self.lock:
            return {
                "emisión_diaria": self.config.emisión_diaria,
                "salario_mínimo": self.config.salario_mínimo,
                "velocidad": self.config.velocidad,
                "informalidad_por_empresa": self.config.informalidad_por_empresa,
            }