# memoria.py
from typing import List, Optional, Tuple
from procesos import Particion, Proceso


class GestorMemoria:
    def __init__(
        self, particiones: Optional[List[Particion]] = None, grado_max: int = 5
    ):
        # Particiones de la consigna: SO=100K reservada, usuario: 250K, 150K, 50K
        if particiones is None:
            particiones = [
                Particion(
                    id_particion=0,
                    base=0,
                    tamaño=100,
                    reservada=True,
                    libre=False,
                    proceso=None,
                    frag_interna=0,
                ),
                Particion(
                    id_particion=1,
                    base=100,
                    tamaño=250,
                    reservada=False,
                    libre=True,
                    proceso=None,
                    frag_interna=0,
                ),
                Particion(
                    id_particion=2,
                    base=350,
                    tamaño=150,
                    reservada=False,
                    libre=True,
                    proceso=None,
                    frag_interna=0,
                ),
                Particion(
                    id_particion=3,
                    base=500,
                    tamaño=50,
                    reservada=False,
                    libre=True,
                    proceso=None,
                    frag_interna=0,
                ),
            ]
        self.particiones: List[Particion] = particiones
        self.grado_max = grado_max
        self.en_memoria = sum(
            0 if (p.reservada or p.libre) else 1 for p in self.particiones
        )
        self.espera_memoria: List[Proceso] = []

    def _particiones_usuario_libres(self) -> List[Particion]:
        return [p for p in self.particiones if not p.reservada and p.libre]

    def _max_tam_usuario(self) -> int:
        return max((p.tamaño for p in self.particiones if not p.reservada), default=0)

    def _best_fit(self, req: int) -> Optional[Particion]:
        candidatas = [p for p in self._particiones_usuario_libres() if p.tamaño >= req]
        if not candidatas:
            return None
        return min(candidatas, key=lambda p: p.tamaño - req)

    def asignar_proceso(self, p: Proceso) -> Optional[Particion]:
        if self.en_memoria >= self.grado_max:
            return None
        part = self._best_fit(p.memoria_requerida)
        if not part:
            return None
        # asignación
        part.libre = False
        part.proceso = p
        part.frag_interna = part.tamaño - p.memoria_requerida
        p.particion_asignada = part.id_particion
        p.estado = "Listo"
        if p.tiempo_restante is None:
            p.tiempo_restante = p.duracion_cpu
        self.en_memoria += 1
        return part

    def intentar_admitir(self, p: Proceso) -> Tuple[bool, str]:
        # reglas de rechazo
        if p.memoria_requerida > self._max_tam_usuario():
            self.espera_memoria.append(p)
            p.estado = "Listo/Suspendido"
            return False, "no_cabe_en_ninguna"
        if self.en_memoria >= self.grado_max:
            self.espera_memoria.append(p)
            p.estado = "Listo/Suspendido"
            return False, "grado_max"

        part = self.asignar_proceso(p)
        if part:
            return True, f"asignado_p{part.id_particion}"
        # no hay partición libre adecuada
        self.espera_memoria.append(p)
        p.estado = "Listo/Suspendido"
        return False, "sin_particion_libre_adecuada"

    def liberar_proceso(self, p: Proceso) -> None:
        if p.particion_asignada is None:
            return
        for part in self.particiones:
            if part.id_particion == p.particion_asignada:
                part.libre = True
                part.proceso = None
                part.frag_interna = 0
                break
        p.particion_asignada = None
        p.estado = "Terminado"
        if self.en_memoria > 0:
            self.en_memoria -= 1
        # reintentos FIFO hasta que no quepa nadie más o se alcance el grado
        i = 0
        while i < len(self.espera_memoria) and self.en_memoria < self.grado_max:
            q = self.espera_memoria[i]
            part = self._best_fit(q.memoria_requerida)
            if part:
                # admitir y sacar de la espera
                part.libre = False
                part.proceso = q
                part.frag_interna = part.tamaño - q.memoria_requerida
                q.particion_asignada = part.id_particion
                q.estado = "Listo"
                if q.tiempo_restante is None:
                    q.tiempo_restante = q.duracion_cpu
                self.en_memoria += 1
                self.espera_memoria.pop(i)
                # no avanzamos i porque la lista se corrió
            else:
                i += 1

    def snapshot_tabla_memoria(self):
        filas = []
        for p in self.particiones:
            nombre_proc = (
                "SO"
                if p.reservada
                else ("Libre" if p.libre else p.proceso.id if p.proceso else "Libre")
            )
            filas.append(
                {
                    "Partición": p.id_particion,
                    "Dirección": p.base,
                    "Tamaño": p.tamaño,
                    "Proceso": nombre_proc,
                    "Frag. interna": p.frag_interna,
                }
            )
        return filas
