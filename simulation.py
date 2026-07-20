# --- simulation.py ---
import snapshot
import state
import threading
import time

from markets import (
    emisión_monetaria,
    mercado_laboral,
    mercado_productos,
)

from estadisticas import actualizar_estadisticas


class Simulación:

    def __init__(self, config):

        self.config = config

        self.estado = state.Estado(config)

        self.corriendo = False

        self.hilo = None

        self.callbacks = []

        self.lock = threading.Lock()


    def agregar_callback(self, callback):

        self.callbacks.append(callback)


    def obtener_snapshot(self):
        with self.lock:
            estadísticas = self.estado.estadisticas
            return snapshot.Snapshot(
                día=self.estado.día,
                salario_medio=(
                    estadísticas.salario_medio[-1]
                    if estadísticas.salario_medio
                    else 0
                ),
                salario_informal_medio=(
                    estadísticas.salario_informal_medio[-1]
                    if estadísticas.salario_informal_medio
                    else 0
                ),
                # Reemplazo de precio_medio por los nuevos atributos:
                precio_lista_medio=(
                    estadísticas.precio_lista_medio[-1]
                    if estadísticas.precio_lista_medio
                    else 0
                ),
                precio_transaccion_medio=(
                    estadísticas.precio_transaccion_medio[-1]
                    if estadísticas.precio_transaccion_medio
                    else 0
                ),
                empleo_formal=(
                    estadísticas.empleo_formal[-1]
                    if estadísticas.empleo_formal
                    else 0
                ),
                empleo_informal=(
                    estadísticas.empleo_informal[-1]
                    if estadísticas.empleo_informal
                    else 0
                ),
                desempleo=(
                    estadísticas.desempleo[-1]
                    if estadísticas.desempleo
                    else 0
                ),
                tasa_emisión=self.config.tasa_emisión,
                salario_mínimo=self.config.salario_mínimo,
                salario_mínimo_automático=self.config.salario_mínimo_automático,
                informalidad_por_empresa=self.config.informalidad_por_empresa,
            )


    def notificar(self):

        snapshot_obj = self.obtener_snapshot()

        for callback in self.callbacks:

            callback(snapshot_obj)


    def step(self):

        with self.lock:

            if self.estado.día >= self.config.días:

                self.corriendo = False

                return False


            self.estado.día += 1

            emisión_monetaria(self.estado)
             
            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            mercado_laboral(self.estado)

            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            mercado_productos(self.estado)

            actualizar_estadisticas(self.estado)


        if self.estado.día % self.config.frecuencia_actualización == 0:

            self.notificar()

        return True


    def ejecutar(self):

        while self.corriendo:

            self.step()

            time.sleep(self.config.velocidad)


    def iniciar(self):

        if self.corriendo:

            return


        self.corriendo = True

        self.hilo = threading.Thread(
            target=self.ejecutar,
            daemon=True
        )

        self.hilo.start()


    def pausar(self):

        self.corriendo = False


    def continuar(self):

        self.iniciar()


    def reset(self):

        with self.lock:

            self.corriendo = False

            self.estado = state.Estado(self.config)


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


    def obtener_parametros(self):

        with self.lock:

            return {
                "emisión_diaria": self.config.emisión_diaria,
                "salario_mínimo": self.config.salario_mínimo,
                "velocidad": self.config.velocidad,
                "informalidad_por_empresa": self.config.informalidad_por_empresa,
            }


    def terminada(self):

        with self.lock:

            return self.estado.día >= self.config.días