# io_metricas.py
import csv
from typing import List, Dict
from procesos import Proceso

def cargar_procesos_csv(path: str) -> List[Proceso]:
    procesos: List[Proceso] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            procesos.append(Proceso(
                id=row["ID"].strip(),
                t_arribo=int(row["Arribo"]),
                duracion_cpu=int(row["RafagaCPU"]),
                memoria_requerida=int(row["Memoria"]),
            ))
    return procesos

def imprimir_tabla(filas: List[Dict], titulo: str = "") -> None:
    if titulo:
        print(f"\n=== {titulo} ===")
    print(f"{'Partición':>9} | {'Dirección':>9} | {'Tamaño':>6} | {'Proceso':>12} | {'Frag. interna':>14}")
    print("-"*9 + "-+-" + "-"*9 + "-+-" + "-"*6 + "-+-" + "-"*12 + "-+-" + "-"*14)
    for f in filas:
        print(f"{f['Partición']:>9} | {f['Dirección']:>9} | {f['Tamaño']:>6} | {f['Proceso']:>12} | {f['Frag. interna']:>14}")

def snapshot_memoria(gestor_memoria) -> None:
    """Imprime la tabla de memoria que exige la consigna (ARRIBO/FIN)."""
    filas = gestor_memoria.snapshot_tabla_memoria()
    imprimir_tabla(filas, "Snapshot Memoria")

def log_evento(tiempo: int, texto: str) -> None:
    print(f"\n[t={tiempo}] {texto}")

def calcular_metricas(lista_procesos: List[Proceso]) -> Dict:
    """
    Stub para métricas finales (completar luego):
    - tiempo de espera promedio
    - tiempo de retorno promedio
    - throughput, etc.
    """
    return {
        "tiempo_espera_prom": None,
        "tiempo_retorno_prom": None,
        "throughput": None,
    }
