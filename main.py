# main.py
# -----------------------------------------------------------
# Punto de entrada de la aplicación.
# -----------------------------------------------------------

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from memoria import GestorMemoria
from procesos import Proceso
from simulacion import ejecutar_simulacion
from io_metricas import cargar_procesos_desde_csv


def parse_args() -> argparse.Namespace:
    """
    Define la CLI:
      --csv <ruta>    Ruta al CSV de procesos (default: procesos.csv)
      --verbose       Imprime eventos y snapshots de memoria
    """
    parser = argparse.ArgumentParser(
        prog="simulador-so",
        description=(
            "Simulador de SO — SRTF con desalojo + memoria con particiones "
            "fijas y Best-Fit."
        ),
    )
    parser.add_argument(
        "--csv",
        default="procesos.csv",
        help="Ruta al archivo CSV con columnas: ID,Arribo,RafagaCPU,Memoria",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra eventos y snapshots durante la ejecución",
    )
    return parser.parse_args()


def main() -> int:
    """
    Orquesta:
      1) Lee args.
      2) Valida existencia del CSV.
      3) Carga procesos.
      4) Construye GestorMemoria.
      5) Ejecuta la simulación.
    """
    args = parse_args()

    if not os.path.isfile(args.csv):
        sys.stderr.write(f"Error: no se encontró el archivo CSV: {args.csv}\n")
        return 1

    try:
        procesos: List[Proceso] = cargar_procesos_desde_csv(args.csv)
        if not procesos:
            sys.stderr.write(
                f"Error de datos: el CSV '{args.csv}' no contiene procesos.\n"
            )
            return 1

        gestor_memoria = GestorMemoria()

        ejecutar_simulacion(
            procesos=procesos,
            gestor_memoria=gestor_memoria,
            verbose=bool(args.verbose),
        )
        return 0

    except (KeyError, ValueError) as e:
        sys.stderr.write(f"Error de datos: {e}\n")
        return 1
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"Error inesperado: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
