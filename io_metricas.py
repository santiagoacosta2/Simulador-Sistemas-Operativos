"""
io_metricas.py
---------------------------------------------
Utilidades de E/S para el simulador de SO:
    - Carga de procesos desde CSV.
    - Logging textual de eventos (opcional).
    - Snapshots de memoria (delegados al GestorMemoria).
---------------------------------------------
"""

from __future__ import annotations

from typing import List
import csv

from procesos import Proceso

# Cabeceras esperadas en el CSV
CSV_HEADERS = ("ID", "Arribo", "RafagaCPU", "Memoria")


# ---------------------------------------------------------------------------
# Helpers internos para parseo y validación
# ---------------------------------------------------------------------------


def _parse_int(campo: str, valor: str, linea: int) -> int:
    """
    Convierte una cadena a entero con mensaje de error claro.
    """
    try:
        return int(valor)
    except ValueError as exc:
        raise ValueError(
            f"CSV línea {linea}: '{campo}' debe ser entero. Valor={valor!r}"
        ) from exc


def _validar_fila(
    id_: str,
    arribo: int,
    rafaga: int,
    memoria: int,
    linea: int,
) -> None:
    """
    Reglas mínimas de validación para una fila de procesos.
    """
    if not id_.strip():
        raise ValueError(f"CSV línea {linea}: 'ID' no puede estar vacío.")
    if arribo < 0:
        raise ValueError(f"CSV línea {linea}: 'Arribo' debe ser >= 0.")
    if rafaga <= 0:
        raise ValueError(f"CSV línea {linea}: 'RafagaCPU' debe ser > 0.")
    if memoria <= 0:
        raise ValueError(f"CSV línea {linea}: 'Memoria' debe ser > 0.")


# ---------------------------------------------------------------------------
# Carga de procesos desde CSV (API principal usada por main.py)
# ---------------------------------------------------------------------------


def cargar_procesos_desde_csv(path: str) -> List[Proceso]:
    """
    Lee un CSV con cabecera (ID, Arribo, RafagaCPU, Memoria)
    y devuelve una lista de Proceso.
    """
    procesos: List[Proceso] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise KeyError("CSV sin cabecera. Se esperaban columnas con nombres.")

        faltantes = [h for h in CSV_HEADERS if h not in reader.fieldnames]
        if faltantes:
            raise KeyError(f"CSV sin columnas requeridas: faltan {faltantes}")

        for i, row in enumerate(reader, start=2):
            id_ = row["ID"].strip()
            arribo = _parse_int("Arribo", row["Arribo"], i)
            rafaga = _parse_int("RafagaCPU", row["RafagaCPU"], i)
            memoria = _parse_int("Memoria", row["Memoria"], i)

            _validar_fila(id_, arribo, rafaga, memoria, i)

            procesos.append(
                Proceso(
                    id=id_,
                    arribo=arribo,
                    rafaga_cpu=rafaga,
                    memoria=memoria,
                )
            )

    return procesos


def cargar_procesos_csv(path: str) -> List[Proceso]:
    """
    Alias de compatibilidad hacia atrás.
    """
    return cargar_procesos_desde_csv(path)


# ---------------------------------------------------------------------------
# Utilidades de logging / snapshots (opcionales)
# ---------------------------------------------------------------------------


def log_evento(tiempo: int, texto: str) -> None:
    """
    Log simple con marca de tiempo.
    """
    print(f"[t={tiempo}] {texto}")


def snapshot_memoria(gestor_memoria) -> None:
    """
    Snapshot de memoria: delega en GestorMemoria.imprimir_estado().
    """
    gestor_memoria.imprimir_estado()