import argparse
from simulacion import Simulador


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="procesos.csv")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Simulador(csv_path=args.csv, verbose=args.verbose).ejecutar()
