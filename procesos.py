# procesos.py
# -----------------------------------------------------------
# Modelos de dominio: Proceso y Particion.
# Se usan dataclasses para simplicidad y legibilidad.
# Incluye validaciones mínimas y valores derivados.
# -----------------------------------------------------------

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proceso:
    """
    Representa un proceso de usuario.

    Atributos obligatorios:
      - id: identificador único lógico (p.ej., "P1").
      - t_arribo: instante de arribo al sistema (entero >= 0).
      - duracion_cpu: ráfaga total de CPU requerida (entero > 0).
      - memoria_requerida: tamaño en K requerido para entrar a memoria (entero > 0).

    Atributos derivados/estado:
      - tiempo_restante: se inicializa con duracion_cpu si no se provee.
      - particion_asignada: id lógico de partición cuando está admitido.
      - estado: ciclo de vida simplificado.
      - t_final: se completa al terminar para métricas (turnaround/espera).
    """

    id: str
    t_arribo: int
    duracion_cpu: int
    memoria_requerida: int

    tiempo_restante: Optional[int] = None
    particion_asignada: Optional[int] = None
    estado: str = "Nuevo"  # Nuevo | Listo | Listo/Suspendido | Ejecutando | Terminado
    t_final: Optional[int] = None  # lo setea el simulador al finalizar

    def __post_init__(self) -> None:
        # Normaliza y valida mínimos
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Proceso.id debe ser un string no vacío.")
        if self.t_arribo < 0:
            raise ValueError("Proceso.t_arribo debe ser >= 0.")
        if self.duracion_cpu <= 0:
            raise ValueError("Proceso.duracion_cpu debe ser > 0.")
        if self.memoria_requerida <= 0:
            raise ValueError("Proceso.memoria_requerida debe ser > 0.")

        # Si no se especifica, el tiempo restante arranca igual a la ráfaga
        if self.tiempo_restante is None:
            self.tiempo_restante = self.duracion_cpu


@dataclass
class Particion:
    """
    Partición de memoria fija.

    Notas:
      - 'reservada=True' solo para la partición del SO.
      - 'libre' indica disponibilidad.
      - 'proceso' referencia al Proceso asignado o None.
      - 'frag_interna' se calcula al asignar con Best-Fit.
    """

    id_particion: int
    base: int  # dirección base (p.ej., 0, 100, 350, 500)
    tamaño: int  # tamaño en K de la partición (se mantiene el nombre utilizado)
    reservada: bool = False
    libre: bool = True
    proceso: Optional[Proceso] = None
    frag_interna: int = 0

    # Sin __post_init__: las validaciones y la gestión de fragmentación
    # se realizan desde el GestorMemoria al momento de asignar/liberar.
