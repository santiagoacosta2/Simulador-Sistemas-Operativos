"""
Módulo de simulación principal del TPI de Sistemas Operativos.

Responsabilidades:
    - Orquestar la simulación de ARRIBOS y FIN_CPU.
    - Coordinar:
        * Gestión de memoria (GestorMemoria).
        * Planificación SRTF con desalojo (SrtfScheduler).
        * Cálculo de métricas por proceso y globales.
        * Impresión de snapshots e informe final.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from memoria import GestorMemoria
from procesos import Proceso
from planificador_srtf import SrtfScheduler, Scheduler


# ---------------------------------------------------------------------------
# Estado por proceso
# ---------------------------------------------------------------------------


@dataclass
class EstadoSimulacion:
    """
    Tracking del ciclo de vida de un proceso.
    """

    tiempo_arribo: int
    tiempo_inicio_cpu: Optional[int] = None
    tiempo_fin: Optional[int] = None
    tiempo_retorno: Optional[int] = None
    tiempo_espera: Optional[int] = None
    # True si fue rechazado definitivamente (NO_CABE_EN_NINGUNA)
    descartado: bool = False


# ---------------------------------------------------------------------------
# Simulador
# ---------------------------------------------------------------------------


class Simulador:
    """
    Orquestador de la simulación CPU + Memoria.
    """

    def __init__(
        self,
        procesos: List[Proceso],
        gestor_memoria: GestorMemoria,
        scheduler: Optional[Scheduler] = None,
        verbose: bool = False,
    ) -> None:
        self._gestor_memoria = gestor_memoria
        self._scheduler: Scheduler = scheduler or SrtfScheduler()

        self._procesos: List[Proceso] = sorted(procesos, key=lambda p: p.arribo)
        self._tiempo_actual: int = 0
        self._indice_siguiente_arribo: int = 0

        self._estado_metricas: Dict[str, EstadoSimulacion] = {
            p.id: EstadoSimulacion(tiempo_arribo=p.arribo) for p in self._procesos
        }

        self._verbose = verbose

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def run(self) -> None:
        while self._hay_trabajo_pendiente():
            tiempo_proximo_arribo = self._tiempo_proximo_arribo()
            tiempo_proximo_fin_cpu = self._tiempo_proximo_fin_cpu()

            tipo_evento, instante_evento = self._resolver_proximo_evento(
                tiempo_proximo_arribo, tiempo_proximo_fin_cpu
            )

            self._avanzar_tiempo_hasta(instante_evento)

            if tipo_evento == "ARRIBO":
                self._procesar_arribos_en_instante(instante_evento)
            elif tipo_evento == "FIN_CPU":
                self._procesar_fin_cpu()
            else:
                raise RuntimeError(f"Evento inválido: {tipo_evento}")

        self._calcular_metricas_finales()
        self._imprimir_resumen_final()

    # ------------------------------------------------------------------
    # Lógica de eventos
    # ------------------------------------------------------------------

    def _hay_trabajo_pendiente(self) -> bool:
        quedan_arribos = self._indice_siguiente_arribo < len(self._procesos)
        proceso_cpu = self._scheduler.proceso_en_cpu()
        hay_listos = self._scheduler.hay_listos()
        return quedan_arribos or proceso_cpu is not None or hay_listos

    def _tiempo_proximo_arribo(self) -> Optional[int]:
        if self._indice_siguiente_arribo >= len(self._procesos):
            return None
        return self._procesos[self._indice_siguiente_arribo].arribo

    def _tiempo_proximo_fin_cpu(self) -> Optional[int]:
        proceso_actual = self._scheduler.proceso_en_cpu()
        if proceso_actual is None:
            return None

        if getattr(proceso_actual, "tiempo_restante", None) is None:
            proceso_actual.tiempo_restante = int(proceso_actual.rafaga_cpu)

        if proceso_actual.tiempo_restante <= 0:
            return self._tiempo_actual

        return self._tiempo_actual + int(proceso_actual.tiempo_restante)

    def _resolver_proximo_evento(
        self,
        tiempo_proximo_arribo: Optional[int],
        tiempo_proximo_fin_cpu: Optional[int],
    ) -> Tuple[str, int]:
        # Solo ARRIBO
        if tiempo_proximo_arribo is not None and tiempo_proximo_fin_cpu is None:
            return "ARRIBO", tiempo_proximo_arribo

        # Solo FIN_CPU
        if tiempo_proximo_arribo is None and tiempo_proximo_fin_cpu is not None:
            return "FIN_CPU", tiempo_proximo_fin_cpu

        # Ninguno → error lógico si todavía hay trabajo
        if tiempo_proximo_arribo is None and tiempo_proximo_fin_cpu is None:
            raise RuntimeError("No hay más eventos pero la simulación sigue activa")

        # Ambos presentes
        assert tiempo_proximo_arribo is not None
        assert tiempo_proximo_fin_cpu is not None

        if tiempo_proximo_fin_cpu < tiempo_proximo_arribo:
            return "FIN_CPU", tiempo_proximo_fin_cpu
        if tiempo_proximo_arribo < tiempo_proximo_fin_cpu:
            return "ARRIBO", tiempo_proximo_arribo

        # Empate: FIN_CPU primero
        return "FIN_CPU", tiempo_proximo_fin_cpu

    # ------------------------------------------------------------------
    # Avance de tiempo
    # ------------------------------------------------------------------

    def _avanzar_tiempo_hasta(self, nuevo_tiempo: int) -> None:
        if nuevo_tiempo < self._tiempo_actual:
            raise ValueError("El tiempo no puede retroceder")

        delta = nuevo_tiempo - self._tiempo_actual
        if delta > 0:
            self._scheduler.avanzar_tiempo(delta)

        self._tiempo_actual = nuevo_tiempo

    # ------------------------------------------------------------------
    # ARRIBOS
    # ------------------------------------------------------------------

    def _procesar_arribos_en_instante(self, instante: int) -> None:
        assert self._tiempo_actual == instante

        while (
            self._indice_siguiente_arribo < len(self._procesos)
            and self._procesos[self._indice_siguiente_arribo].arribo == instante
        ):
            proceso = self._procesos[self._indice_siguiente_arribo]
            self._indice_siguiente_arribo += 1

            admitido, motivo = self._gestor_memoria.intentar_admitir_proceso(
                proceso=proceso,
                tiempo=self._tiempo_actual,
            )

            if admitido:
                if not hasattr(proceso, "tiempo_restante"):
                    proceso.tiempo_restante = int(proceso.rafaga_cpu)

                self._scheduler.agregar_proceso(proceso, self._tiempo_actual)

                estado = self._estado_metricas[proceso.id]
                if estado.tiempo_inicio_cpu is None:
                    if self._scheduler.proceso_en_cpu() is proceso:
                        estado.tiempo_inicio_cpu = self._tiempo_actual

            else:
                if motivo == "NO_CABE_EN_NINGUNA":
                    estado = self._estado_metricas[proceso.id]
                    estado.descartado = True

                if self._verbose:
                    print(
                        f"[t={self._tiempo_actual}] ARRIBO {proceso.id} NO admitido: {motivo}"
                    )

        if self._verbose:
            self._imprimir_snapshot(evento="ARRIBO", tiempo=self._tiempo_actual)

    # ------------------------------------------------------------------
    # FIN_CPU
    # ------------------------------------------------------------------

    def _procesar_fin_cpu(self) -> None:
        proceso_terminado = self._scheduler.sacar_proceso_actual()
        if proceso_terminado is None:
            raise RuntimeError("FIN_CPU disparado sin proceso en CPU")

        estado = self._estado_metricas[proceso_terminado.id]
        estado.tiempo_fin = self._tiempo_actual

        procesos_ahora_admitidos = self._gestor_memoria.liberar_y_reintentar(
            proceso_terminado=proceso_terminado,
            tiempo=self._tiempo_actual,
        )

        for proc in procesos_ahora_admitidos:
            if not hasattr(proc, "tiempo_restante"):
                proc.tiempo_restante = int(proc.rafaga_cpu)

            self._scheduler.agregar_proceso(proc, self._tiempo_actual)

            estado_proc = self._estado_metricas[proc.id]
            if estado_proc.tiempo_inicio_cpu is None:
                if self._scheduler.proceso_en_cpu() is proc:
                    estado_proc.tiempo_inicio_cpu = self._tiempo_actual

        proceso_actual = self._scheduler.proceso_en_cpu()
        if proceso_actual is not None:
            estado_actual = self._estado_metricas[proceso_actual.id]
            if estado_actual.tiempo_inicio_cpu is None:
                estado_actual.tiempo_inicio_cpu = self._tiempo_actual

        if self._verbose:
            self._imprimir_snapshot(evento="FIN_CPU", tiempo=self._tiempo_actual)

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------

    def _calcular_metricas_finales(self) -> None:
        """
        Calcula tiempos de retorno y espera para cada proceso NO descartado.

        Fórmulas:
            retorno = tiempo_fin - tiempo_arribo
            espera  = retorno - rafaga_cpu
        """
        for proceso in self._procesos:
            estado = self._estado_metricas[proceso.id]

            if estado.descartado:
                continue

            if estado.tiempo_fin is None:
                raise RuntimeError(f"Proceso {proceso.id} no terminó")

            estado.tiempo_retorno = estado.tiempo_fin - estado.tiempo_arribo
            estado.tiempo_espera = estado.tiempo_retorno - proceso.rafaga_cpu

    def _imprimir_resumen_final(self) -> None:
        """
        Imprime resumen por proceso + métricas globales
        (solo para procesos que realmente se ejecutaron).
        """
        filas = []
        for proceso in self._procesos:
            estado = self._estado_metricas[proceso.id]

            if estado.descartado:
                continue

            tiempo_respuesta = None
            if estado.tiempo_inicio_cpu is not None:
                tiempo_respuesta = estado.tiempo_inicio_cpu - estado.tiempo_arribo

            filas.append(
                {
                    "id": proceso.id,
                    "arribo": estado.tiempo_arribo,
                    "inicio_cpu": estado.tiempo_inicio_cpu,
                    "fin": estado.tiempo_fin,
                    "retorno": estado.tiempo_retorno,
                    "espera": estado.tiempo_espera,
                    "respuesta": tiempo_respuesta,
                    "rafaga": proceso.rafaga_cpu,
                }
            )

        n = len(filas)
        if n == 0:
            print("\n===== RESUMEN FINAL DE MÉTRICAS =====")
            print("No hay procesos ejecutados (todos fueron descartados).")
            print("=====================================\n")
            return

        suma_retorno = sum(f["retorno"] for f in filas if f["retorno"] is not None)
        suma_espera = sum(f["espera"] for f in filas if f["espera"] is not None)
        suma_respuesta = sum(
            f["respuesta"] for f in filas if f["respuesta"] is not None
        )
        promedio_retorno = suma_retorno / n if n > 0 else 0.0
        promedio_espera = suma_espera / n if n > 0 else 0.0
        promedio_respuesta = suma_respuesta / n if n > 0 else 0.0

        tiempo_total = max(f["fin"] for f in filas if f["fin"] is not None)
        throughput = n / tiempo_total if tiempo_total and tiempo_total > 0 else 0.0

        print("\n===== RESUMEN FINAL DE MÉTRICAS =====")
        for f in filas:
            print(
                f"Proceso {f['id']}: arribo={f['arribo']}, "
                f"inicio_cpu={f['inicio_cpu']}, fin={f['fin']}, "
                f"retorno={f['retorno']}, espera={f['espera']}, "
                f"respuesta={f['respuesta']}"
            )
        print("-------------------------------------")
        print(f"Promedio retorno   : {promedio_retorno:.2f}")
        print(f"Promedio espera    : {promedio_espera:.2f}")
        print(f"Promedio respuesta : {promedio_respuesta:.2f}")
        print(f"Throughput         : {throughput:.3f} procesos/unidad de tiempo")
        print("=====================================\n")

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def _imprimir_snapshot(self, evento: str, tiempo: int) -> None:
        print(f"\n===== SNAPSHOT t={tiempo} evento={evento} =====")

        # CPU actual
        proceso_cpu = self._scheduler.proceso_en_cpu()
        if proceso_cpu is None:
            print("CPU: libre")
        else:
            print(
                f"CPU: {proceso_cpu.id} (restante={proceso_cpu.tiempo_restante})"
            )

        # Cola de listos (si el scheduler expone listar_listos)
        if hasattr(self._scheduler, "listar_listos"):
            listos = self._scheduler.listar_listos()  # type: ignore[attr-defined]
            if listos:
                cadena = ", ".join(f"{pid}(rest={rest})" for pid, rest in listos)
                print(f"Cola de listos (SRTF): {cadena}")
            else:
                print("Cola de listos (SRTF): <vacía>")

        # Estado de memoria (incluye cola de espera)
        self._gestor_memoria.imprimir_estado()
        print("======================================\n")


# ---------------------------------------------------------------------------
# Wrapper para main.py
# ---------------------------------------------------------------------------


def ejecutar_simulacion(
    procesos: List[Proceso],
    gestor_memoria: GestorMemoria,
    verbose: bool = False,
) -> None:
    simulador = Simulador(
        procesos=procesos,
        gestor_memoria=gestor_memoria,
        scheduler=SrtfScheduler(),
        verbose=verbose,
    )
    simulador.run()