# simulacion.py
from typing import List, Optional

import io_metricas as io
from memoria import GestorMemoria
from planificador import PlanificadorSRTF
from procesos import Proceso


class Simulador:
    def __init__(self, csv_path: str, verbose: bool = False):
        self.csv_path = csv_path
        self.verbose = verbose
        self.procesos: List[Proceso] = io.cargar_procesos_csv(csv_path)
        # precondición simple: llegan ordenados por arribo
        self.procesos.sort(key=lambda p: p.t_arribo)
        self.memoria = GestorMemoria()  # particiones fijas de la consigna
        self.planificador = PlanificadorSRTF()
        self.tiempo = 0
        self.en_ejecucion: Optional[Proceso] = None
        self.terminados: List[Proceso] = []

    def _arribo(self, p: Proceso) -> None:
        ok, motivo = self.memoria.intentar_admitir(p)
        estado = "Listo" if ok else "Listo/Suspendido"
        if self.verbose:
            io.log_evento(
                self.tiempo,
                f"ARRIBO {p.id} (mem={p.memoria_requerida}K) -> {estado} [{motivo}]",
            )
            io.snapshot_memoria(self.memoria)
        if ok:
            self.planificador.agregar(p)

    def _fin_proceso(self, p: Proceso) -> None:
        # Demo: mostrar liberación y reintentos en cascada.
        p.estado = "Terminado"
        self.memoria.liberar_proceso(p)
        self.terminados.append(p)
        if self.verbose:
            io.log_evento(
                self.tiempo,
                "FIN_CPU {pid} -> liberar partición + reintentos FIFO+Best-Fit".format(
                    pid=p.id
                ),
            )
            io.snapshot_memoria(self.memoria)

    def ejecutar(self) -> None:
        """
        Demo mínima:
        - Dispara ARRIBO en orden para mostrar memoria y ready.
        - Simula un FIN de uno admitido para mostrar admisiones en cascada.
        """
        # ARRIBOS
        for p in self.procesos:
            self.tiempo = p.t_arribo
            self._arribo(p)

        # elegir uno en memoria (no SO) para finalizar y disparar cascada
        candidato: Optional[Proceso] = None
        for part in self.memoria.particiones:
            if not part.reservada and not part.libre and part.proceso:
                candidato = part.proceso
                break

        if candidato:
            self.tiempo += 1
            self._fin_proceso(candidato)
        else:
            if self.verbose:
                io.log_evento(self.tiempo, "No hay proceso para terminar en la demo.")

        # Si más adelante agregás métricas, podés imprimir aquí:
        # if hasattr(io, "imprimir_resumen"):
        #     io.imprimir_resumen(self.terminados, self.tiempo)
