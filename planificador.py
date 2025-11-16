# planificador.py
# -----------------------------------------------------------
# Planificador SRTF simple, útil para tests o ejemplos aislados.
# -----------------------------------------------------------

from __future__ import annotations

import heapq
from typing import List, Optional, Tuple

from procesos import Proceso


class PlanificadorSRTF:
    """
    Cola de listos con prioridad por menor tiempo_restante.
    """

    def __init__(self) -> None:
        self._heap: List[Tuple[int, int, Proceso]] = []
        self._seq: int = 0

    def _ensure_tiempo_restante(self, proceso: Proceso) -> None:
        if not hasattr(proceso, "tiempo_restante") or proceso.tiempo_restante is None:
            proceso.tiempo_restante = int(proceso.rafaga_cpu)

    def agregar(self, proceso: Proceso) -> None:
        self._ensure_tiempo_restante(proceso)
        heapq.heappush(self._heap, (proceso.tiempo_restante, self._seq, proceso))
        self._seq += 1

    def reencolar(self, proceso: Proceso) -> None:
        self._ensure_tiempo_restante(proceso)
        heapq.heappush(self._heap, (proceso.tiempo_restante, self._seq, proceso))
        self._seq += 1

    def obtener_siguiente(self) -> Optional[Proceso]:
        if not self._heap:
            return None
        _, _, p = heapq.heappop(self._heap)
        return p

    def ver_top(self) -> Optional[Proceso]:
        if not self._heap:
            return None
        return self._heap[0][2]

    def preempt_si_corresponde(self, actual: Optional[Proceso], nuevo: Proceso) -> bool:
        if actual is None:
            return False
        self._ensure_tiempo_restante(nuevo)
        self._ensure_tiempo_restante(actual)
        return nuevo.tiempo_restante < actual.tiempo_restante

    def esta_vacio(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)