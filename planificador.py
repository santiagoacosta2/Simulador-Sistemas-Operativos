# planificador.py
# -----------------------------------------------------------
# Planificador SRTF (Shortest Remaining Time First) con desalojo.
# Implementa una cola de listos basada en heap:
#   - Prioridad: menor tiempo_restante primero.
#   - Desempate estable por un contador incremental (_seq).
#
# Interfaz:
#   agregar(p)                  -> encola p (si no tiene tiempo_restante, usa la ráfaga)
#   obtener_siguiente()         -> saca el próximo a ejecutar o None
#   ver_top()                   -> mira el próximo sin sacarlo o None
#   preempt_si_corresponde(a,n) -> True si n debe desalojar a a (por tiempo restante menor)
#   reencolar(p)                -> reingresa p a la cola (tras desalojo o tick de CPU)
#   esta_vacio()                -> True si no hay listos
#   __len__()                   -> cantidad de procesos en cola
#
# Nota: Este módulo no “ejecuta” CPU ni descuenta tiempo. Solo ordena.
#       El simulador es quien ajusta p.tiempo_restante y decide llamar
#       a reencolar/obtener/preempt, etc.
# -----------------------------------------------------------

import heapq
from typing import List, Optional, Tuple

from procesos import Proceso


class PlanificadorSRTF:
    """
    Cola de listos con prioridad por menor tiempo_restante.
    No asume precondiciones fuertes: si p.tiempo_restante es None,
    lo inicializa con p.duracion_cpu.
    """

    def __init__(self) -> None:
        # Heap de tuplas (tiempo_restante, seq, Proceso).
        # 'seq' garantiza estabilidad: primero en entrar, primero en desempatar.
        self._heap: List[Tuple[int, int, Proceso]] = []
        self._seq: int = 0

    # ---------------
    # Operaciones CRUD
    # ---------------

    def agregar(self, proceso: Proceso) -> None:
        """
        Encola un proceso en la cola de listos SRTF.
        Si no tiene tiempo_restante, lo inicializa con su ráfaga total.
        """
        if proceso.tiempo_restante is None:
            proceso.tiempo_restante = proceso.duracion_cpu
        heapq.heappush(self._heap, (proceso.tiempo_restante, self._seq, proceso))
        self._seq += 1

    def reencolar(self, proceso: Proceso) -> None:
        """
        Reingresa 'proceso' a la cola con su tiempo_restante actual.
        Usar cuando fue desalojado o tras consumir un tick parcial.
        """
        if proceso.tiempo_restante is None:
            proceso.tiempo_restante = proceso.duracion_cpu
        heapq.heappush(self._heap, (proceso.tiempo_restante, self._seq, proceso))
        self._seq += 1

    def obtener_siguiente(self) -> Optional[Proceso]:
        """
        Saca el próximo a ejecutar según SRTF.
        Devuelve None si la cola está vacía.
        """
        if not self._heap:
            return None
        _, _, p = heapq.heappop(self._heap)
        return p

    def ver_top(self) -> Optional[Proceso]:
        """
        Observa el próximo a ejecutar sin retirarlo del heap.
        Útil para tests o decisiones sin consumo.
        """
        if not self._heap:
            return None
        return self._heap[0][2]

    # -----------------
    # Lógica de desalojo
    # -----------------

    def preempt_si_corresponde(self, actual: Optional[Proceso], nuevo: Proceso) -> bool:
        """
        Indica si 'nuevo' debe desalojar a 'actual'.
        Regla SRTF: desalojar si nuevo.tiempo_restante < actual.tiempo_restante.
        Si 'actual' es None, no hay a quién desalojar.
        """
        if actual is None:
            return False
        nr = (
            nuevo.tiempo_restante
            if nuevo.tiempo_restante is not None
            else nuevo.duracion_cpu
        )
        ar = (
            actual.tiempo_restante
            if actual.tiempo_restante is not None
            else actual.duracion_cpu
        )
        return nr < ar

    # --------------
    # Consultas varias
    # --------------

    def esta_vacio(self) -> bool:
        """True si no hay procesos listos."""
        return len(self._heap) == 0

    def __len__(self) -> int:
        """Cantidad de procesos en la cola de listos."""
        return len(self._heap)
