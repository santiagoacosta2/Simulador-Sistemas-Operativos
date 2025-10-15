# io_metricas.py
# ---------------------------------------------
# Utilidades de E/S: carga de CSV, logging de eventos,
# snapshots de memoria y métricas/resumen final.
# Todo comentado y con validaciones mínimas.
# ---------------------------------------------

from typing import List, Dict, Tuple
import csv

from prettytable import PrettyTable  # tabla bonita para resumen final
from procesos import Proceso


# ---------------------------
# Carga de procesos desde CSV
# ---------------------------

CSV_HEADERS = ("ID", "Arribo", "RafagaCPU", "Memoria")


def _parse_int(campo: str, valor: str, linea: int) -> int:
    """Convierte a int con error claro."""
    try:
        return int(valor)
    except ValueError as e:
        raise ValueError(
            f"CSV línea {linea}: '{campo}' debe ser entero. Valor={valor!r}"
        ) from e


def _validar_fila(id_: str, arribo: int, rafaga: int, memoria: int, linea: int) -> None:
    """Reglas mínimas de validación para la primera entrega."""
    if not id_.strip():
        raise ValueError(f"CSV línea {linea}: 'ID' no puede estar vacío.")
    if arribo < 0:
        raise ValueError(f"CSV línea {linea}: 'Arribo' debe ser >= 0.")
    if rafaga <= 0:
        raise ValueError(f"CSV línea {linea}: 'RafagaCPU' debe ser > 0.")
    if memoria <= 0:
        raise ValueError(f"CSV línea {linea}: 'Memoria' debe ser > 0.")
    # Nota: si se quiere limitar por tamaño máx de partición de usuario, se puede chequear aquí.


def cargar_procesos_csv(path: str) -> List[Proceso]:
    """
    Lee un CSV con cabecera (ID, Arribo, RafagaCPU, Memoria)
    y devuelve una lista de Proceso ya tipada.

    Errores:
      - Levanta ValueError con línea y campo si hay dato inválido.
      - Levanta KeyError si faltan columnas requeridas.
    """
    procesos: List[Proceso] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Verifica cabeceras requeridas
        faltantes = [h for h in CSV_HEADERS if h not in reader.fieldnames]
        if faltantes:
            raise KeyError(f"CSV sin columnas requeridas: faltan {faltantes}")

        for i, row in enumerate(reader, start=2):  # empieza en 2 por la cabecera
            id_ = row["ID"].strip()
            arribo = _parse_int("Arribo", row["Arribo"], i)
            rafaga = _parse_int("RafagaCPU", row["RafagaCPU"], i)
            memoria = _parse_int("Memoria", row["Memoria"], i)
            _validar_fila(id_, arribo, rafaga, memoria, i)

            procesos.append(
                Proceso(
                    id=id_,
                    t_arribo=arribo,
                    duracion_cpu=rafaga,
                    memoria_requerida=memoria,
                )
            )
    return procesos


# ---------------------------------
# Impresión de tablas y snapshots
# ---------------------------------


def imprimir_tabla(filas: List[Dict], titulo: str = "") -> None:
    """
    Imprime una tabla simple alineada en texto plano.
    Espera diccionarios con claves: Partición, Dirección, Tamaño, Proceso, Frag. interna
    """
    if titulo:
        print(f"\n=== {titulo} ===")

    # Encabezado
    print(
        f"{'Partición':>9} | {'Dirección':>9} | {'Tamaño':>6} | {'Proceso':>12} | {'Frag. interna':>14}"
    )
    print(
        "-" * 9
        + "-+-"
        + "-" * 9
        + "-+-"
        + "-" * 6
        + "-+-"
        + "-" * 12
        + "-+-"
        + "-" * 14
    )

    # Filas
    for f in filas:
        print(
            f"{f['Partición']:>9} | {f['Dirección']:>9} | {f['Tamaño']:>6} | {f['Proceso']:>12} | {f['Frag. interna']:>14}"
        )


def snapshot_memoria(gestor_memoria) -> None:
    """
    Pide al gestor de memoria su snapshot (como lista de dicts)
    y lo imprime con el formato exigido por la consigna.
    """
    filas = gestor_memoria.snapshot_tabla_memoria()
    imprimir_tabla(filas, "Snapshot Memoria")


def log_evento(tiempo: int, texto: str) -> None:
    """Loguea un evento con marca de tiempo simulada."""
    print(f"\n[t={tiempo}] {texto}")


# ----------------
# Métricas finales
# ----------------


def _metricas_por_proceso(p: Proceso) -> Tuple[int, int]:
    """
    Devuelve (turnaround, espera) para un proceso terminado.
    Requiere que el simulador haya seteado p.t_final.
    """
    # turnaround = fin - arribo
    ta = p.t_final - p.t_arribo
    # espera = turnaround - CPU efectiva
    espera = ta - p.duracion_cpu
    return ta, espera


def calcular_metricas(lista_procesos: List[Proceso], t_fin: int) -> Dict[str, float]:
    """
    Calcula métricas globales simples:
      - tiempo_espera_prom
      - tiempo_retorno_prom (turnaround)
      - throughput (proc terminados / tiempo total simulado)

    Retorna un dict con los valores (floats).
    """
    n = len(lista_procesos)
    if n == 0:
        return {
            "tiempo_espera_prom": 0.0,
            "tiempo_retorno_prom": 0.0,
            "throughput": 0.0,
        }

    sum_ta = 0
    sum_esp = 0
    for p in lista_procesos:
        ta, esp = _metricas_por_proceso(p)
        sum_ta += ta
        sum_esp += esp

    prom_ta = sum_ta / n
    prom_esp = sum_esp / n
    thr = (n / t_fin) if t_fin else 0.0

    return {
        "tiempo_espera_prom": prom_esp,
        "tiempo_retorno_prom": prom_ta,
        "throughput": thr,
    }


def imprimir_resumen(procesos: List[Proceso], t_fin: int) -> None:
    """
    Imprime:
      - Tabla por proceso: Arribo, CPU, Fin, Turnaround, Espera.
      - Promedios y throughput.
    """
    tb = PrettyTable(["Proceso", "Arribo", "CPU", "Fin", "Turnaround", "Espera"])
    for p in procesos:
        ta, esp = _metricas_por_proceso(p)
        tb.add_row([p.id, p.t_arribo, p.duracion_cpu, p.t_final, ta, esp])
    print(tb)

    m = calcular_metricas(procesos, t_fin)
    print(
        "Promedios -> Turnaround: {:.2f}  Espera: {:.2f}  Throughput: {:.3f}".format(
            m["tiempo_retorno_prom"], m["tiempo_espera_prom"], m["throughput"]
        )
    )
