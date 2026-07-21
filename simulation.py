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

            # 3. Consumir las funciones del módulo de la versión cargada
            self.modulo_version.emisión_monetaria(self.estado)
             
            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            self.modulo_version.mercado_laboral(self.estado)

            self.estado.aleatorio.shuffle(self.estado.trabajadores)

            self.modulo_version.mercado_productos(self.estado)

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
            self.config.velocidad_streamlit = valor


    def obtener_parametros(self):

        with self.lock:

            return {
                "emisión_diaria": self.config.emisión_diaria,
                "salario_mínimo": self.config.salario_mínimo,
                "velocidad": self.config.velocidad,
                "informalidad_por_empresa": self.config.informalidad_por_empresa,
            }