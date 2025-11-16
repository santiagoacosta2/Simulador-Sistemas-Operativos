"""
Modelo de proceso para el simulador de Sistemas Operativos.

Responsabilidades:
    - Representar los datos básicos de un proceso:
        * id lógico
        * instante de arribo al sistema
        * duración total de CPU (ráfaga)
        * memoria requerida
    - Mantener el tiempo restante de CPU durante la simulación.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Proceso:
    """
    Representa un proceso del sistema.

    Campos:
        id:
            Identificador del proceso (columna 'ID' del CSV).
        arribo:
            Instante en el que el proceso arriba al sistema
            (columna 'Arribo' del CSV).
        rafaga_cpu:
            Duración total de CPU que necesita el proceso
            (columna 'RafagaCPU' del CSV).
        memoria:
            Memoria requerida en KB
            (columna 'Memoria' del CSV).
        tiempo_restante:
            Tiempo de CPU que le falta al proceso.
            Se inicializa en rafaga_cpu y se va descontando.
    """

    id: str
    arribo: int
    rafaga_cpu: int
    memoria: int
    tiempo_restante: int = field(init=False)

    def __post_init__(self) -> None:
        """
        Inicializa tiempo_restante con el valor de rafaga_cpu.
        """
        self.tiempo_restante = int(self.rafaga_cpu)

    @classmethod
    def desde_csv(
        cls,
        id_str: str,
        arribo_str: str,
        rafaga_str: str,
        memoria_str: str,
    ) -> "Proceso":
        """
        Helper para crear un Proceso directamente desde strings del CSV.
        """
        return cls(
            id=id_str.strip(),
            arribo=int(arribo_str),
            rafaga_cpu=int(rafaga_str),
            memoria=int(memoria_str),
        )