from snapshot import Snapshot
import threading
import time

from state import Estado

from markets import (
    emisión_monetaria,
    mercado_laboral,
    mercado_productos,
)

from estadisticas import actualizar_estadisticas


class Simulación:

    def __init__(self, config):

        self.config = config

        self.estado = Estado(config)

        self.corriendo = False

        self.hilo = None

        self.callbacks = []

        self.lock = threading.Lock()


    def agregar_callback(self, callback):

        self.callbacks.append(callback)


    def obtener_snapshot(self):

        with self.lock:

            estadísticas = self.estado.estadisticas

            return Snapshot(

                día=self.estado.día,

                salario_medio=(
                    estadísticas.salario_medio[-1]
                    if estadísticas.salario_medio
                    else 0
                ),

                precio_medio=(
                    estadísticas.precio_medio[-1]
                    if estadísticas.precio_medio
                    else 0
                ),

                emisión_diaria=self.config.emisión_diaria,

                salario_mínimo=self.config.salario_mínimo
            )


    def notificar(self):

        snapshot = self.obtener_snapshot()

        for callback in self.callbacks:

            callback(snapshot)


    def step(self):

        with self.lock:

            if self.estado.día >= self.config.días:

                self.corriendo = False

                return False


            self.estado.día += 1

            emisión_monetaria(self.estado)

            mercado_laboral(self.estado)

            mercado_productos(self.estado)

            actualizar_estadisticas(self.estado)


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

            self.estado = Estado(self.config)


        self.notificar()


    def cambiar_emisión(self, valor):

        with self.lock:

            self.config.emisión_diaria = valor


    def cambiar_salario_mínimo(self, valor):

        with self.lock:

            self.config.salario_mínimo = valor


    def cambiar_velocidad(self, valor):

        with self.lock:

            self.config.velocidad = valor


    def obtener_parametros(self):

        with self.lock:

            return {
                "emisión_diaria": self.config.emisión_diaria,
                "salario_mínimo": self.config.salario_mínimo,
                "velocidad": self.config.velocidad,
            }


    def terminada(self):

        with self.lock:

            return self.estado.día >= self.config.días