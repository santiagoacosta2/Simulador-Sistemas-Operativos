# main.py
from simulacion import Simulador

if __name__ == "__main__":
    sim = Simulador("procesos.csv")
    sim.ejecutar()
