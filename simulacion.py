# simulacion.py
# -----------------------------------------------------------
# Simulador “Entrega 1”: demo de ARRIBO + FIN_CPU en memoria
# con particiones fijas y Best-Fit. Control de salida por
# --verbose y resumen final de métricas.
#
# Nota: es una DEMO de flujo de memoria. El ciclo de CPU con
# SRTF y política de empates se integrará en la siguiente etapa.
# -----------------------------------------------------------

from typing import List, Optional

import io_metricas as io
from memoria import GestorMemoria
from planificador import PlanificadorSRTF
from procesos import Proceso


class Simulador:
    """
    Orquesta la simulación:
      - Lee procesos desde CSV.
      - Gestiona memoria (Best-Fit con grado de multiprogramación).
      - Encola en ready usando un planificador SRTF (aún sin ciclo de CPU).
      - Imprime eventos/snapshots si verbose.
      - Emite métricas finales por proceso.
    """

    def __init__(self, csv_path: str, verbose: bool = False):
        # Entrada de usuario
        self.csv_path = csv_path
        self.verbose = verbose

        # Procesos: se cargan y se ordenan por arribo
        self.procesos: List[Proceso] = io.cargar_procesos_csv(csv_path)
        self.procesos.sort(key=lambda p: p.t_arribo)

        # Subsistemas
        self.memoria = GestorMemoria()  # particiones fijas de consigna
        self.planificador = PlanificadorSRTF()  # cola ready SRTF

        # Estado global
        self.tiempo: int = 0
        self.en_ejecucion: Optional[Proceso] = None  # reservado para próxima etapa
        self.terminados: List[Proceso] = []  # para métricas finales

    # -------------------------
    # Eventos de la DEMO
    # -------------------------

    def _arribo(self, p: Proceso) -> None:
        """
        Evento de llegada:
          - Intenta admitir en memoria con Best-Fit (respeta grado).
          - Si entra, va a ready (SRTF).
          - Log y snapshot solo si verbose.
        """
        ok, motivo = self.memoria.intentar_admitir(p)
        estado = "Listo" if ok else "Listo/Suspendido"

        if self.verbose:
            io.log_evento(
                self.tiempo,
                f"ARRIBO {p.id} (mem={p.memoria_requerida}K) -> {estado} [{motivo}]",
            )
            io.snapshot_memoria(self.memoria)

        if ok:
            # A la cola de listos del SRTF. En la próxima etapa,
            # el ciclo de CPU decidirá si preempta al que está ejecutando.
            self.planificador.agregar(p)

    def _fin_proceso(self, p: Proceso) -> None:
        """
        Evento de fin de CPU (DEMO):
          - Marca terminado, registra t_final para métricas,
            libera memoria y dispara reintentos de espera FIFO.
          - Log y snapshot solo si verbose.
        """
        p.estado = "Terminado"
        p.t_final = self.tiempo  # necesario para turnaround/espera
        self.memoria.liberar_proceso(p)
        self.terminados.append(p)

        if self.verbose:
            io.log_evento(
                self.tiempo,
                f"FIN_CPU {p.id} -> liberar partición + reintentos FIFO+Best-Fit",
            )
            io.snapshot_memoria(self.memoria)

    # -------------------------
    # Bucle de la DEMO actual
    # -------------------------

    def ejecutar(self) -> None:
        """
        DEMO mínima para la entrega 1:
          1) Dispara todos los ARRIBO ordenados por t_arribo.
          2) Finaliza “uno” que esté en memoria (no SO) para
             mostrar la cascada de admisiones tras liberar.
          3) Imprime el resumen de métricas por proceso.
        """
        # 1) ARRIBOS en orden
        for p in self.procesos:
            self.tiempo = p.t_arribo
            self._arribo(p)

        # 2) Elegir un candidato actualmente en memoria (no SO) y finalizarlo
        candidato: Optional[Proceso] = None
        for part in self.memoria.particiones:
            if not part.reservada and not part.libre and part.proceso:
                candidato = part.proceso
                break

        if candidato:
            # Avanza el reloj un tick para reportar un FIN luego de los ARRIBO
            self.tiempo += 1
            self._fin_proceso(candidato)
        else:
            if self.verbose:
                io.log_evento(self.tiempo, "No hay proceso para terminar en la demo.")

        # 3) Resumen final (tabla por proceso + promedios)
        #    Si no hubo “FIN”, la tabla puede estar vacía; es válido.
        io.imprimir_resumen(self.terminados, self.tiempo)

        # -----------------------------------------------
        # NOTA de política futura (dejar documentado aquí):
        # Si en el ciclo completo de simulación se diera
        #   t_prox_arr == t_fin_cpu
        # se priorizará procesar FIN_CPU primero, luego ARRIBO.
        # Esto se implementará al integrar el ciclo SRTF real.
        # -----------------------------------------------
