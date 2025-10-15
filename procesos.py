from dataclasses import dataclass
from typing import Optional


@dataclass
class Proceso:
    id: str
    t_arribo: int
    duracion_cpu: int
    memoria_requerida: int
    tiempo_restante: Optional[int] = None
    particion_asignada: Optional[int] = None
    estado: str = "Nuevo"  # Nuevo | Listo | Listo/Suspendido | Ejecutando | Terminado


@dataclass
class Particion:
    id_particion: int
    base: int  # dirección de comienzo (p.ej., 100, 350, 500)
    tamaño: int
    reservada: bool = False  # True solo para la del SO (100K)
    libre: bool = True
    proceso: Optional[Proceso] = None
    frag_interna: int = 0  # para la tabla
