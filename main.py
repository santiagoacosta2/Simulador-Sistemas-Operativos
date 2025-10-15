# main.py
# -----------------------------------------------------------
# Punto de entrada de la aplicación.
# - Parseo de argumentos de línea de comandos.
# - Construcción y ejecución del Simulador.
# - Mensajes claros ante errores (CSV inválido, etc.).
# -----------------------------------------------------------

import argparse
import os
import sys

from simulacion import Simulador


def parse_args() -> argparse.Namespace:
    """
    Define la CLI:
      --csv <ruta>    Ruta al CSV de procesos (default: procesos.csv)
      --verbose       Imprime eventos y snapshots de memoria
    """
    parser = argparse.ArgumentParser(
        prog="simulador-so",
        description="Simulador de SO — Entrega 1: memoria con particiones fijas y demo ARRIBO/FIN.",
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
      3) Ejecuta la simulación.
    Retorna código de salida (0 ok, 1 error).
    """
    args = parse_args()

    # Validación mínima de la ruta CSV
    if not os.path.isfile(args.csv):
        sys.stderr.write(f"Error: no se encontró el archivo CSV: {args.csv}\n")
        return 1

    try:
        Simulador(csv_path=args.csv, verbose=args.verbose).ejecutar()
        return 0
    except (KeyError, ValueError) as e:
        # Errores de formato/validación de CSV u otros valores inválidos
        sys.stderr.write(f"Error de datos: {e}\n")
        return 1
    except Exception as e:  # noqa: BLE001  (mostramos cualquier otro error inesperado)
        sys.stderr.write(f"Error inesperado: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
