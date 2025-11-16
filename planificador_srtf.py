"""
Módulo de planificación SRTF (Shortest Remaining Time First) con desalojo.

Responsabilidades:
    - Mantener la cola de listos ordenada por menor tiempo_restante.
    - Decidir desalojos cuando llega un proceso más corto.
    - Exponer un pequeño snapshot de la cola de listos para diagnóstico.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Optional, Protocol, List, Tuple, Any

ProcesoLike = Any


class Scheduler(Protocol):
    def agregar_proceso(self, proceso: ProcesoLike, tiempo_actual: int) -> None: ...
    def avanzar_tiempo(self, delta: int) -> None: ...
    def proceso_en_cpu(self) -> Optional[ProcesoLike]: ...
    def sacar_proceso_actual(self) -> Optional[ProcesoLike]: ...
    def hay_listos(self) -> bool: ...


@dataclass(order=True)
class _EntradaCola:
    """
    Entrada interna del heap de SRTF.

    Orden:
        - tiempo_restante (ascendente)
        - orden_llegada
        - secuencia (para estabilidad)
    """

    tiempo_restante: int
    orden_llegada: int
    secuencia: int
    proceso: ProcesoLike = field(compare=False)


class SrtfScheduler(Scheduler):
    """
    Implementación de SRTF con desalojo.

    Estado:
        - _proceso_actual: proceso en CPU (o None).
        - _cola_listos: heap con procesos listos ordenados por tiempo restante.
        - _historial_cambios: log de eventos de planificación (opcional).
    """

    def __init__(self) -> None:
        self._cola_listos: List[_EntradaCola] = []
        self._proceso_actual: Optional[ProcesoLike] = None
        self._tiempo_actual: int = 0
        self._secuencia: int = 0
        self._historial_cambios: List[Tuple[int, str, str]] = []

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def agregar_proceso(self, proceso: ProcesoLike, tiempo_actual: int) -> None:
        """
        Ingresa un proceso al sistema de planificación.

        Si no hay nadie en CPU, entra directo.
        Si hay alguien, se decide si hay desalojo por SRTF.
        """
        self._tiempo_actual = tiempo_actual

        if not hasattr(proceso, "tiempo_restante"):
            proceso.tiempo_restante = int(proceso.rafaga_cpu)

        if self._proceso_actual is None:
            self._proceso_actual = proceso
            self._registrar_evento("ENTRA_CPU", getattr(proceso, "id", "??"))
            return

        tiempo_actual_restante = int(self._proceso_actual.tiempo_restante)
        nuevo_restante = int(proceso.tiempo_restante)

        if nuevo_restante < tiempo_actual_restante:
            # Desalojo
            self._encolar(self._proceso_actual, tiempo_actual_restante, tiempo_actual)
            self._registrar_evento("DESALOJADO", getattr(self._proceso_actual, "id", "??"))
            self._proceso_actual = proceso
            self._registrar_evento("ENTRA_CPU", getattr(proceso, "id", "??"))
        else:
            # Solo entra en cola de listos
            self._encolar(proceso, nuevo_restante, tiempo_actual)

    def avanzar_tiempo(self, delta: int) -> None:
        """
        Avanza el tiempo global y descuenta CPU del proceso actual.
        """
        if self._proceso_actual is None:
            return
        if delta < 0:
            raise ValueError("delta no puede ser negativo")

        self._tiempo_actual += delta
        self._proceso_actual.tiempo_restante -= delta
        if self._proceso_actual.tiempo_restante < 0:
            self._proceso_actual.tiempo_restante = 0

    def proceso_en_cpu(self) -> Optional[ProcesoLike]:
        """
        Devuelve el proceso actual en CPU (o None).
        """
        return self._proceso_actual

    def sacar_proceso_actual(self) -> Optional[ProcesoLike]:
        """
        Marca fin de CPU del proceso actual y carga el siguiente de la cola de listos.
        """
        terminado = self._proceso_actual
        if terminado is not None:
            self._registrar_evento("SALE_CPU", getattr(terminado, "id", "??"))

        self._proceso_actual = self._siguiente_de_cola()

        if self._proceso_actual is not None:
            self._registrar_evento("ENTRA_CPU", getattr(self._proceso_actual, "id", "??"))

        return terminado

    def hay_listos(self) -> bool:
        """
        True si hay procesos en la cola de listos.
        """
        return bool(self._cola_listos)

    # ------------------------------------------------------------------
    # Internos de cola
    # ------------------------------------------------------------------

    def _encolar(
        self,
        proceso: ProcesoLike,
        tiempo_restante: int,
        tiempo_actual: int,
    ) -> None:
        self._secuencia += 1
        entrada = _EntradaCola(
            tiempo_restante=tiempo_restante,
            orden_llegada=tiempo_actual,
            secuencia=self._secuencia,
            proceso=proceso,
        )
        heapq.heappush(self._cola_listos, entrada)
        self._registrar_evento("EN_COLA", getattr(proceso, "id", "??"))

    def _siguiente_de_cola(self) -> Optional[ProcesoLike]:
        if not self._cola_listos:
            return None
        entrada = heapq.heappop(self._cola_listos)
        return entrada.proceso

    # ------------------------------------------------------------------
    # Snapshot de la cola de listos
    # ------------------------------------------------------------------

    def listar_listos(self) -> List[Tuple[str, int]]:
        """
        Devuelve una vista compacta de la cola de listos:
            [(id_proceso, tiempo_restante), ...]
        en el orden actual del heap.
        """
        resultado: List[Tuple[str, int]] = []
        for entrada in self._cola_listos:
            proc = entrada.proceso
            pid = getattr(proc, "id", "??")
            tr = getattr(proc, "tiempo_restante", None)
            if tr is None:
                tr = getattr(proc, "rafaga_cpu", 0)
            resultado.append((pid, int(tr)))
        return resultado

    # ------------------------------------------------------------------
    # Historial de planificación (opcional, para debug)
    # ------------------------------------------------------------------

    def _registrar_evento(self, evento: str, id_proceso: str) -> None:
        self._historial_cambios.append((self._tiempo_actual, evento, id_proceso))

    @property
    def tiempo_actual(self) -> int:
        return self._tiempo_actual

    @property
    def historial_cambios(self) -> List[Tuple[int, str, str]]:
        return list(self._historial_cambios)
