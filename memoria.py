"""
Gestor de memoria con particiones fijas + Best-Fit + grado de multiprogramación.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Any

from prettytable import PrettyTable


@dataclass
class Particion:
    """
    Representa una partición de memoria principal.
    """

    id_particion: str
    base: int
    tamanio: int
    es_so: bool = False
    proceso: Optional[Any] = None

    @property
    def esta_libre(self) -> bool:
        return self.proceso is None

    @property
    def memoria_ocupada(self) -> int:
        if self.proceso is None:
            return 0
        return int(self.proceso.memoria)

    @property
    def fragmentacion_interna(self) -> int:
        if self.proceso is None:
            return 0
        return self.tamanio - self.memoria_ocupada


class GestorMemoria:
    """
    Encapsula TODA la lógica de gestión de memoria con particiones fijas.

    Configuración:
        - 100K SO.
        - 250K, 150K, 50K usuario.
        - Grado de multiprogramación máximo = 5.
    """

    def __init__(self, grado_multiprogramacion_max: int = 5) -> None:
        self._particiones: List[Particion] = [
            Particion(id_particion="SO", base=0, tamanio=100, es_so=True),
            Particion(id_particion="U1", base=100, tamanio=250),
            Particion(id_particion="U2", base=350, tamanio=150),
            Particion(id_particion="U3", base=500, tamanio=50),
        ]

        self._grado_max = grado_multiprogramacion_max
        self._en_memoria_usuario = 0
        self._cola_espera: List[Any] = []

    @property
    def particiones(self) -> List[Particion]:
        return self._particiones

    @property
    def cola_espera(self) -> List[Any]:
        return list(self._cola_espera)

    @property
    def grado_multiprogramacion_actual(self) -> int:
        return self._en_memoria_usuario

    @property
    def grado_multiprogramacion_max(self) -> int:
        return self._grado_max

    # ------------------------------------------------------------------
    # API para Simulador
    # ------------------------------------------------------------------

    def intentar_admitir_proceso(self, proceso: Any, tiempo: int) -> Tuple[bool, str]:
        """
        Intenta admitir un proceso usando Best-Fit.

        Retorna (bool, motivo):
            True, "ASIGNADO"
            False, "NO_CABE_EN_NINGUNA"
            False, "GRADO_MAXIMO"
            False, "SIN_PARTICION_LIBRE_ADECUADA"
        """
        tamanio_proceso = int(proceso.memoria)

        if not self._puede_caber_en_alguna_particion(tamanio_proceso):
            return False, "NO_CABE_EN_NINGUNA"

        if self._en_memoria_usuario >= self._grado_max:
            self._cola_espera.append(proceso)
            return False, "GRADO_MAXIMO"

        particion = self._buscar_best_fit_libre(tamanio_proceso)
        if particion is None:
            self._cola_espera.append(proceso)
            return False, "SIN_PARTICION_LIBRE_ADECUADA"

        self._asignar_particion(particion, proceso)
        print(
            f"[t={tiempo}] Proceso {proceso.id} asignado a partición {particion.id_particion} "
            f"(tamaño={particion.tamanio}K, pedido={tamanio_proceso}K)"
        )

        return True, "ASIGNADO"

    def liberar_y_reintentar(
        self,
        proceso_terminado: Any,
        tiempo: int,
    ) -> List[Any]:
        """
        Libera memoria del proceso terminado y reintenta cola de espera (FIFO).
        """
        self._liberar_particion_de(proceso_terminado, tiempo)

        admitidos: List[Any] = []
        cola_original = list(self._cola_espera)
        self._cola_espera.clear()

        for proceso in cola_original:
            if self._en_memoria_usuario >= self._grado_max:
                self._cola_espera.append(proceso)
                continue

            tamanio_proceso = int(proceso.memoria)

            if not self._puede_caber_en_alguna_particion(tamanio_proceso):
                print(
                    f"[t={tiempo}] Proceso {proceso.id} descartado de espera: "
                    f"no cabe en ninguna partición."
                )
                continue

            particion = self._buscar_best_fit_libre(tamanio_proceso)
            if particion is None:
                self._cola_espera.append(proceso)
                continue

            self._asignar_particion(particion, proceso)
            admitidos.append(proceso)
            print(
                f"[t={tiempo}] Proceso {proceso.id} admitido desde cola de espera "
                f"a partición {particion.id_particion} (tamaño={particion.tamanio}K)"
            )

        return admitidos

    # ------------------------------------------------------------------
    # Lógica interna
    # ------------------------------------------------------------------

    def _particiones_usuario(self) -> List[Particion]:
        return [p for p in self._particiones if not p.es_so]

    def _puede_caber_en_alguna_particion(self, tamanio_proceso: int) -> bool:
        max_tamanio = max(p.tamanio for p in self._particiones_usuario())
        return tamanio_proceso <= max_tamanio

    def _buscar_best_fit_libre(self, tamanio_proceso: int) -> Optional[Particion]:
        mejor: Optional[Particion] = None
        mejor_sobrante: Optional[int] = None

        for particion in self._particiones_usuario():
            if not particion.esta_libre:
                continue
            if particion.tamanio < tamanio_proceso:
                continue

            sobrante = particion.tamanio - tamanio_proceso
            if mejor is None or sobrante < mejor_sobrante:  # type: ignore[operator]
                mejor = particion
                mejor_sobrante = sobrante

        return mejor

    def _asignar_particion(self, particion: Particion, proceso: Any) -> None:
        if not particion.esta_libre:
            raise RuntimeError(
                f"Intento de asignar a partición ocupada: {particion.id_particion}"
            )

        particion.proceso = proceso
        if not particion.es_so:
            self._en_memoria_usuario += 1

    def _liberar_particion_de(self, proceso: Any, tiempo: int) -> None:
        for particion in self._particiones_usuario():
            if particion.proceso is proceso:
                print(
                    f"[t={tiempo}] Proceso {proceso.id} libera partición {particion.id_particion} "
                    f"(tamaño={particion.tamanio}K)"
                )
                particion.proceso = None
                self._en_memoria_usuario -= 1
                if self._en_memoria_usuario < 0:
                    self._en_memoria_usuario = 0
                return

        print(
            f"[t={tiempo}] Aviso: se intentó liberar memoria de {getattr(proceso, 'id', '?')} "
            f"pero no se encontró partición asignada."
        )

    # ------------------------------------------------------------------
    # Visualización
    # ------------------------------------------------------------------

    def imprimir_estado(self) -> None:
        tabla = PrettyTable()
        tabla.field_names = [
            "Partición",
            "Base",
            "Tamaño(K)",
            "Proceso",
            "Ocupada(K)",
            "Frag. interna(K)",
        ]

        for particion in self._particiones:
            if particion.proceso is None:
                id_proceso = "-"
                ocupada = 0
                frag = 0
            else:
                id_proceso = getattr(particion.proceso, "id", "?")
                ocupada = particion.memoria_ocupada
                frag = particion.fragmentacion_interna

            tabla.add_row(
                [
                    particion.id_particion,
                    particion.base,
                    particion.tamanio,
                    id_proceso,
                    ocupada,
                    frag,
                ]
            )

        print("=== Estado de la memoria ===")
        print(tabla)
        print(
            f"Grado multiprogramación: {self._en_memoria_usuario}"
            f"/{self._grado_max}, en espera: {len(self._cola_espera)}"
        )
        print("============================\n")