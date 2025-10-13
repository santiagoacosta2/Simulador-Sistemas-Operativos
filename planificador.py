# planificador.py
import heapq
from typing import Optional
from procesos import Proceso

class PlanificadorSRTF:
    """
    Cola de listos con prioridad por menor tiempo_restante.
    Solo la interfaz mínima para integrarse con el simulador.
    """
    def __init__(self):
        self._heap = []
        self._seq = 0  # desempate estable

    def agregar(self, proceso: Proceso) -> None:
        """Encola un proceso 'Listo'."""
        if proceso.tiempo_restante is None:
            proceso.tiempo_restante = proceso.duracion_cpu
        heapq.heappush(self._heap, (proceso.tiempo_restante, self._seq, proceso))
        self._seq += 1

    def obtener_siguiente(self) -> Optional[Proceso]:
        """Saca el próximo a ejecutar (o None si vacío)."""
        if not self._heap:
            return None
        _, _, p = heapq.heappop(self._heap)
        return p

    def preempt_si_corresponde(self, actual: Optional[Proceso], nuevo: Proceso) -> bool:
        """
        Si llega 'nuevo' más corto que 'actual', devuelve True (debe desalojar).
        En este stub no cambiamos 'actual' aquí; solo avisamos.
        """
        if actual is None:
            return False
        nr = nuevo.tiempo_restante or nuevo.duracion_cpu
        ar = actual.tiempo_restante or actual.duracion_cpu
        return nr < ar

    def esta_vacio(self) -> bool:
        return len(self._heap) == 0
