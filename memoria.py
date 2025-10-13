from collections import deque
from typing import List, Optional, Deque
from procesos import Proceso, Particion

class GestorMemoria:
    def __init__(self):
        # Layout EXACTO de la consigna:
        # P0: SO 100K (reservada, no asignable)
        # P1: 250K, P2: 150K, P3: 50K
        self.particiones: List[Particion] = [
            Particion(0, base=0,   tamaño=100, reservada=True, libre=False),         # SO
            Particion(1, base=100, tamaño=250),
            Particion(2, base=350, tamaño=150),
            Particion(3, base=500, tamaño=50),
        ]
        self.grado_max = 5
        self.en_memoria = 0                      # procesos admitidos (no cuenta SO)
        self.espera_memoria: Deque[Proceso] = deque()

    def intentar_admitir(self, proceso: Proceso) -> tuple[bool, str]:
        if self.en_memoria >= self.grado_max:
            proceso.estado = "Listo/Suspendido"
            self.espera_memoria.append(proceso)
            return False, "grado_max"

        # Si jamás cabe en ninguna partición util (no reservada)
        if proceso.memoria_requerida > max(p.tamaño for p in self.particiones if not p.reservada):
            proceso.estado = "Listo/Suspendido"
            self.espera_memoria.append(proceso)
            return False, "no_cabe_en_ninguna"

        mejor = self._buscar_best_fit(proceso.memoria_requerida)
        if mejor is None:
            proceso.estado = "Listo/Suspendido"
            self.espera_memoria.append(proceso)
            return False, "sin_particion_libre_adecuada"

        self._ocupar(mejor, proceso)
        proceso.tiempo_restante = proceso.tiempo_restante or proceso.duracion_cpu
        proceso.estado = "Listo"
        self.en_memoria += 1
        return True, f"asignado_p{mejor.id_particion}"

    def liberar_proceso(self, proceso: Proceso) -> Optional[Particion]:
        if proceso.particion_asignada is None:
            return None
        part = self._particion_por_id(proceso.particion_asignada)
        if part is None:
            return None
        self._liberar(part)
        self.en_memoria -= 1
        self._admitir_en_espera()
        return part

    # ---------- utilidades internas ----------
    def _buscar_best_fit(self, req: int) -> Optional[Particion]:
        mejor = None
        min_sobrante = None
        for p in self.particiones:
            if p.reservada:              # nunca asignar el SO
                continue
            if p.libre and p.tamaño >= req:
                sobrante = p.tamaño - req
                if (mejor is None) or (sobrante < min_sobrante):
                    mejor = p
                    min_sobrante = sobrante
        return mejor

    def _ocupar(self, particion: Particion, proceso: Proceso) -> None:
        particion.libre = False
        particion.proceso = proceso
        particion.frag_interna = particion.tamaño - proceso.memoria_requerida
        proceso.particion_asignada = particion.id_particion

    def _liberar(self, particion: Particion) -> None:
        particion.libre = True
        particion.frag_interna = 0
        if particion.proceso:
            particion.proceso.particion_asignada = None
        particion.proceso = None

    def _particion_por_id(self, idp: int) -> Optional[Particion]:
        return next((p for p in self.particiones if p.id_particion == idp), None)

    def _admitir_en_espera(self) -> None:
        if not self.espera_memoria:
            return
        # FIFO + repetir mientras haya espacio y cupo de grado
        hubo_cambio = True
        while hubo_cambio and self.en_memoria < self.grado_max:
            hubo_cambio = False
            for _ in range(len(self.espera_memoria)):
                proc = self.espera_memoria[0]
                mejor = self._buscar_best_fit(proc.memoria_requerida)
                if mejor and self.en_memoria < self.grado_max:
                    self.espera_memoria.popleft()
                    self._ocupar(mejor, proc)
                    proc.estado = "Listo"
                    self.en_memoria += 1
                    hubo_cambio = True
                else:
                    self.espera_memoria.rotate(-1)

    # ---------- para snapshots que pide la cátedra ----------
    def snapshot_tabla_memoria(self) -> list[dict]:
        """
        Devuelve filas con: id_part, base, tamaño, id_proceso (o 'Libre'), fragmentacion_interna
        para que el módulo de I/O/Métricas lo imprima en cada ARRIBO/FIN.
        """
        filas = []
        for p in self.particiones:
            filas.append({
                "Partición": p.id_particion,
                "Dirección": p.base,
                "Tamaño": p.tamaño,
                "Proceso": p.proceso.id if p.proceso else ("SO" if p.reservada else "Libre"),
                "Frag. interna": p.frag_interna if (p.proceso and not p.reservada) else 0
            })
        return filas
