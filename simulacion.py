# simulacion.py
from typing import List
from procesos import Proceso
from memoria import GestorMemoria
from planificador import PlanificadorSRTF
from io_metricas import cargar_procesos_csv, snapshot_memoria, log_evento

class Simulador:
    def __init__(self, csv_path: str):
        self.procesos: List[Proceso] = cargar_procesos_csv(csv_path)
        # Orden por arribo (precondición simple)
        self.procesos.sort(key=lambda p: p.t_arribo)
        self.memoria = GestorMemoria()      # particiones fijas de la consigna
        self.planificador = PlanificadorSRTF()
        self.tiempo = 0
        self.en_ejecucion = None  # Proceso o None

    def _arribo(self, p: Proceso):
        ok, motivo = self.memoria.intentar_admitir(p)
        estado = "Listo" if ok else "Listo/Suspendido"
        log_evento(self.tiempo, f"ARRIBO {p.id} (mem={p.memoria_requerida}K) -> {estado} [{motivo}]")
        # Si entró a memoria, pasa a ready:
        if ok:
            self.planificador.agregar(p)
        snapshot_memoria(self.memoria)

    def _fin_proceso(self, p: Proceso):
        # En una simulación real esto se gatilla cuando p.tiempo_restante llega a 0.
        # Aquí lo usamos para mostrar la liberación y admisiones en cascada.
        p.estado = "Terminado"
        self.memoria.liberar_proceso(p)
        log_evento(self.tiempo, f"FIN_CPU {p.id} -> liberar partición + reintentos FIFO+Best-Fit")
        snapshot_memoria(self.memoria)

    def ejecutar(self):
        """
        Demo mínima:
        - Dispara todos los ARRIBO en orden (solo para mostrar memoria y ready).
        - Simula un FIN de uno que haya entrado, para mostrar liberación en cascada.
        """
        # ARRIBOS
        for p in self.procesos:
            self.tiempo = p.t_arribo
            self._arribo(p)

        # Elegimos terminar uno que efectivamente esté en memoria (no el SO).
        candidato = None
        for part in self.memoria.particiones:
            if not part.reservada and not part.libre and part.proceso:
                candidato = part.proceso
                break

        if candidato:
            # su FIN al final de los arribos, solo para demostrar la cascada
            self.tiempo += 1
            self._fin_proceso(candidato)
        else:
            log_evento(self.tiempo, "No hay proceso para terminar en la demo.")
