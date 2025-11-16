# presentacion.py
# -----------------------------------------------------------
# Modo "presentación" del TPI.
#
# Objetivo:
#   - Guiar la explicación del simulador en una defensa oral.
#   - Mostrar la arquitectura (módulos y responsabilidades).
#   - Mostrar el código fuente de los módulos clave con líneas.
#   - Ejecutar la simulación real y mostrar los snapshots.
#
# Uso:
#   python presentacion.py
#
# Luego, si querés un .exe:
#   pyinstaller --onefile presentacion.py
# -----------------------------------------------------------

from __future__ import annotations

import os
import textwrap

from io_metricas import cargar_procesos_desde_csv
from memoria import GestorMemoria
from simulacion import ejecutar_simulacion

# -----------------------------------------------------------
# Utilidades de presentación
# -----------------------------------------------------------


def _clear_screen() -> None:
    """
    Limpia la consola (mejor visualización durante la defensa).
    Funciona en Windows y en sistemas tipo Unix.
    """
    os.system("cls" if os.name == "nt" else "clear")


def _esperar_enter(mensaje: str = "Presioná ENTER para continuar...") -> None:
    """
    Pausa la presentación hasta que el usuario presiona ENTER.
    """
    input(f"\n{mensaje}")


def _print_titulo(titulo: str) -> None:
    """
    Imprime un título grande con separadores.
    """
    print("=" * len(titulo))
    print(titulo)
    print("=" * len(titulo))


def _print_bloque(texto: str) -> None:
    """
    Imprime un bloque de texto con indentación prolija.
    """
    print(textwrap.dedent(texto).strip())
    print()


def _mostrar_codigo(ruta: str, titulo: str) -> None:
    """
    Muestra el contenido de un archivo fuente con números de línea.

    Ejemplo de uso en la defensa:
        - Mostrar memoria.py y explicar la clase GestorMemoria.
    """
    _clear_screen()
    _print_titulo(f"Código: {titulo}")
    ruta_absoluta = os.path.abspath(ruta)

    if not os.path.isfile(ruta_absoluta):
        print(f"(No se encontró el archivo: {ruta_absoluta})")
        _esperar_enter()
        return

    print(f"Archivo: {ruta_absoluta}\n")

    with open(ruta_absoluta, "r", encoding="utf-8") as f:
        for i, linea in enumerate(f, start=1):
            # Imprime número de línea a la izquierda
            print(f"{i:03}: {linea.rstrip()}")

    _esperar_enter("Fin del archivo. Presioná ENTER para seguir...")


# -----------------------------------------------------------
# Secciones de la presentación
# -----------------------------------------------------------


def seccion_arquitectura_general() -> None:
    _clear_screen()
    _print_titulo("Arquitectura general del simulador")

    _print_bloque(
        """
    El simulador está dividido en módulos, cada uno con una responsabilidad clara:

    - procesos.py
        Define la clase Proceso, que representa un proceso del sistema:
        id, tiempo de arribo, ráfaga de CPU, memoria requerida y tiempo restante.

    - io_metricas.py
        Se encarga de la entrada/salida:
        * Carga de procesos desde un CSV (ID, Arribo, RafagaCPU, Memoria).
        * Validación de datos.
        * Algunas utilidades de logging (no críticas para la lógica).

    - memoria.py
        Modela la memoria principal con particiones fijas:
        * Partición SO (100K) y tres particiones de usuario (250K, 150K, 50K).
        * Política de asignación Best-Fit.
        * Control del grado de multiprogramación (máx. 5 procesos en memoria de usuario).
        * Cola de espera para procesos que no pueden entrar en memoria temporalmente.

    - planificador_srtf.py
        Implementa el planificador de CPU SRTF con desalojo:
        * Mantiene un proceso en CPU.
        * Mantiene una cola de listos basada en un heap, ordenada por menor tiempo restante.
        * Decide cuándo desalojar el proceso actual si llega uno más corto.

    - simulacion.py
        Es el orquestador del sistema:
        * Avanza el reloj de simulación.
        * Procesa eventos de ARRIBO y FIN_CPU.
        * Coordina memoria + CPU.
        * Calcula métricas finales (tiempo de retorno, espera, respuesta, throughput).
        * Imprime snapshots del estado del sistema.

    - main.py
        Es el punto de entrada:
        * Lee argumentos de la línea de comandos.
        * Carga procesos desde el CSV.
        * Crea el GestorMemoria.
        * Llama a ejecutar_simulacion con o sin modo verbose.
    """
    )

    _esperar_enter()


def seccion_modulos_clave() -> None:
    """
    Muestra código de los módulos clave, uno por uno.
    Podés ir comentando mientras se ve el código en pantalla.
    """
    # 1) procesos.py
    _mostrar_codigo("procesos.py", "Modelo de Proceso")

    # 2) memoria.py
    _mostrar_codigo("memoria.py", "Gestor de Memoria (particiones fijas + Best-Fit)")

    # 3) planificador_srtf.py
    _mostrar_codigo("planificador_srtf.py", "Planificador SRTF con desalojo")

    # 4) simulacion.py
    _mostrar_codigo("simulacion.py", "Orquestador de eventos y métricas")

    # 5) main.py (opcional, suele ser corto)
    _mostrar_codigo("main.py", "Punto de entrada (CLI)")


def seccion_demo_simulacion() -> None:
    """
    Ejecuta la simulación real con verbose=True y explica qué se está viendo.
    """
    _clear_screen()
    _print_titulo("Demo de simulación (con snapshots)")

    _print_bloque(
        """
    Ahora se va a ejecutar la simulación real, usando el mismo código
    que se entrega en el TPI:

    - Se carga procesos.csv.
    - Se crea el GestorMemoria con particiones fijas y Best-Fit.
    - Se usa el planificador SRTF con desalojo.
    - Se imprime un snapshot en cada ARRIBO y FIN_CPU, donde se ve:
        * Proceso en CPU y tiempo restante.
        * Cola de listos ordenada por tiempo restante.
        * Estado de la memoria (particiones, proceso asignado, fragmentación).
        * Cola de espera de memoria.
    """
    )

    _esperar_enter("Presioná ENTER para ejecutar la simulación...")

    # Ejecutar la simulación con el CSV por defecto (procesos.csv)
    procesos = cargar_procesos_desde_csv("procesos.csv")
    gestor = GestorMemoria()
    ejecutar_simulacion(procesos=procesos, gestor_memoria=gestor, verbose=True)

    _esperar_enter("Simulación finalizada. Presioná ENTER para volver al menú...")


def seccion_resumen_final() -> None:
    _clear_screen()
    _print_titulo("Resumen de puntos fuertes del diseño")

    _print_bloque(
        """
    Puntos a destacar en la defensa:

    - Separación clara de responsabilidades:
        * Cada módulo tiene un rol específico (modelo, memoria, CPU, simulación, CLI).
        * Facilita pruebas, mantenimiento y extensión.

    - Diseño del planificador:
        * Implementado como un Scheduler independiente.
        * SRTF con desalojo implementado sobre una estructura de datos eficiente (heap).
        * La simulación no depende de los detalles internos del heap.

    - Gestión de memoria:
        * Particiones fijas con Best-Fit.
        * Control explícito del grado de multiprogramación.
        * Cola de espera FIFO para procesos que no entran en memoria.
        * Manejo explícito del caso “NO_CABE_EN_NINGUNA”, sin romper la simulación.

    - Métricas y trazabilidad:
        * Se registran tiempos de arribo, inicio de CPU y fin para cada proceso.
        * Se calculan: tiempo de retorno, espera, respuesta y throughput.
        * El modo verbose ofrece una trazabilidad paso a paso del estado del sistema.

    - Preparado para extensión:
        * Se podría cambiar el algoritmo de planificación (otro Scheduler).
        * Se podrían definir otros esquemas de memoria (otro GestorMemoria).
        * Sin necesidad de reescribir toda la simulación.
    """
    )

    _esperar_enter("Fin de la presentación guiada. Presioná ENTER para salir...")


# -----------------------------------------------------------
# Menú principal
# -----------------------------------------------------------


def menu_principal() -> None:
    while True:
        _clear_screen()
        _print_titulo("Presentación interactiva del simulador de SO (TPI)")

        print("Elegí una opción:\n")
        print("  1) Ver arquitectura general")
        print("  2) Ver código de los módulos clave")
        print("  3) Ejecutar demo de simulación (con snapshots)")
        print("  4) Ver resumen para la defensa")
        print("  0) Salir")

        opcion = input("\nOpción: ").strip()

        if opcion == "1":
            seccion_arquitectura_general()
        elif opcion == "2":
            seccion_modulos_clave()
        elif opcion == "3":
            seccion_demo_simulacion()
        elif opcion == "4":
            seccion_resumen_final()
        elif opcion == "0":
            break
        else:
            _print_bloque("Opción inválida.")
            _esperar_enter()


if __name__ == "__main__":
    menu_principal()
