# memoria.py
# -----------------------------------------------------------
# Gestor de memoria con particiones fijas.
# - SO reservado: 100K (id_particion=0, base=0), siempre ocupado.
# - Usuario: 250K (id=1, base=100), 150K (id=2, base=350), 50K (id=3, base=500)
# - Política de asignación: Best-Fit.
# - Grado de multiprogramación configurable (default=5).
# - Cola FIFO de espera por memoria y reintentos al liberar.
#
# Interfaz pública usada por el simulador/tests:
#   - intentar_admitir(p) -> (ok: bool, motivo: str)
#   - liberar_proceso(p) -> None
#   - snapshot_tabla_memoria() -> List[dict]  (para imprimir tabla)
#   - asignar_proceso(p) -> Particion|None    (uso interno)
# -----------------------------------------------------------

from typing import List, Optional, Tuple

from procesos import Particion, Proceso


class GestorMemoria:
    def __init__(
        self, particiones: Optional[List[Particion]] = None, grado_max: int = 5
    ):
        """
        Si no se provee una lista de particiones, se crean las de la consigna.
        'grado_max' limita la cantidad de procesos de usuario simultáneamente en memoria.
        """
        if particiones is None:
            particiones = [
                # SO reservado: aparece como ocupado, sin proceso asociado.
                Particion(
                    id_particion=0,
                    base=0,
                    tamaño=100,
                    reservada=True,
                    libre=False,
                    proceso=None,
                    frag_interna=0,
                ),
                # Usuario
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
        self.grado_max: int = grado_max

        # Conteo de procesos de usuario actualmente en memoria
        self.en_memoria: int = sum(
            0 if (p.reservada or p.libre) else 1 for p in self.particiones
        )

        # Cola FIFO de procesos esperando por memoria
        self.espera_memoria: List[Proceso] = []

    # -------------------------
    # Helpers internos (privados)
    # -------------------------

    def _particiones_usuario_libres(self) -> List[Particion]:
        """Devuelve particiones de usuario libres."""
        return [p for p in self.particiones if not p.reservada and p.libre]

    def _max_tam_usuario(self) -> int:
        """Máximo tamaño disponible entre particiones de usuario (independiente del estado libre/ocupado)."""
        return max((p.tamaño for p in self.particiones if not p.reservada), default=0)

    def _best_fit(self, req: int) -> Optional[Particion]:
        """
        Selecciona la partición libre más ajustada (mínima fragmentación interna)
        que pueda albergar 'req'. Si no hay, devuelve None.
        """
        candidatas = [p for p in self._particiones_usuario_libres() if p.tamaño >= req]
        if not candidatas:
            return None
        # Minimiza (tamaño - requerido)
        return min(candidatas, key=lambda p: p.tamaño - req)

    # -------------------------
    # API principal
    # -------------------------

    def asignar_proceso(self, p: Proceso) -> Optional[Particion]:
        """
        Intenta asignar 'p' a una partición libre por Best-Fit.
        Respeta el 'grado_max'. Devuelve la partición usada o None.
        """
        if self.en_memoria >= self.grado_max:
            return None

        part = self._best_fit(p.memoria_requerida)
        if not part:
            return None

        # Asignación efectiva
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
        """
        Intenta admitir 'p' en memoria. Retorna (ok, motivo):
          - (False, "no_cabe_en_ninguna") si requiere más que la partición de usuario más grande.
          - (False, "grado_max") si ya se alcanzó el grado de multiprogramación.
          - (False, "sin_particion_libre_adecuada") si no hay libre que ajuste (queda en espera).
          - (True,  "asignado_pX") si se asigna (X = id de partición).
        En caso de False, el proceso pasa a estado 'Listo/Suspendido' y entra a espera FIFO.
        """
        # Rechazo inmediato: pide más que cualquier partición de usuario
        if p.memoria_requerida > self._max_tam_usuario():
            self.espera_memoria.append(p)
            p.estado = "Listo/Suspendido"
            return False, "no_cabe_en_ninguna"

        # Rechazo temporal: límite de grado
        if self.en_memoria >= self.grado_max:
            self.espera_memoria.append(p)
            p.estado = "Listo/Suspendido"
            return False, "grado_max"

        # Intento real de asignación
        part = self.asignar_proceso(p)
        if part:
            return True, f"asignado_p{part.id_particion}"

        # No hay partición libre adecuada por tamaño en este momento
        self.espera_memoria.append(p)
        p.estado = "Listo/Suspendido"
        return False, "sin_particion_libre_adecuada"

    def liberar_proceso(self, p: Proceso) -> None:
        """
        Libera la partición ocupada por 'p' y reintenta admitir procesos en espera (FIFO),
        respetando Best-Fit y el grado de multiprogramación.
        """
        if p.particion_asignada is None:
            return

        # Liberación de la partición
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

        # Reintentos FIFO:
        # Se itera con índice 'i' para poder remover del medio sin perder el recorrido.
        i = 0
        while i < len(self.espera_memoria) and self.en_memoria < self.grado_max:
            q = self.espera_memoria[i]
            part = self._best_fit(q.memoria_requerida)

            if part:
                # Admitir q y sacarlo de espera (no avanzar i porque la lista se compacta)
                part.libre = False
                part.proceso = q
                part.frag_interna = part.tamaño - q.memoria_requerida

                q.particion_asignada = part.id_particion
                q.estado = "Listo"
                if q.tiempo_restante is None:
                    q.tiempo_restante = q.duracion_cpu

                self.en_memoria += 1
                self.espera_memoria.pop(i)
            else:
                # No hay partición libre adecuada para q; intentar con el siguiente en la cola
                i += 1

    # -------------------------
    # Snapshot para impresión
    # -------------------------

    def snapshot_tabla_memoria(self):
        """
        Devuelve una lista de dicts con el estado de cada partición,
        con las claves esperadas por la rutina de impresión:
          - Partición, Dirección, Tamaño, Proceso, Frag. interna
        """
        filas = []
        for p in self.particiones:
            # Nombre del proceso en la tabla:
            if p.reservada:
                nombre_proc = "SO"
            else:
                if p.libre:
                    nombre_proc = "Libre"
                else:
                    nombre_proc = p.proceso.id if p.proceso else "Libre"

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
