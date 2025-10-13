# test_memoria_consigna.py
# Requiere: procesos.py y memoria.py (con GestorMemoria de la consigna)
from procesos import Proceso
from memoria import GestorMemoria

def imprimir_tabla(filas, titulo=""):
    if titulo:
        print(f"\n=== {titulo} ===")
    print(f"{'Partición':>9} | {'Dirección':>9} | {'Tamaño':>6} | {'Proceso':>10} | {'Frag. interna':>14}")
    print("-"*9 + "-+-" + "-"*9 + "-+-" + "-"*6 + "-+-" + "-"*10 + "-+-" + "-"*14)
    for f in filas:
        print(f"{f['Partición']:>9} | {f['Dirección']:>9} | {f['Tamaño']:>6} | {f['Proceso']:>10} | {f['Frag. interna']:>14}")

def main():
    # Inicializa particiones exactas de la consigna dentro del GestorMemoria
    gm = GestorMemoria()

    # Lote de procesos de prueba (ID, Arribo, RafagaCPU, Memoria)
    # Nota: P4 (300K) no cabe en ninguna partición de usuario (250/150/50).
    procesos = [
        Proceso("P1", 0, 8, 90),
        Proceso("P2", 1, 5, 240),
        Proceso("P3", 2, 4, 80),
        Proceso("P4", 3, 7, 300),  # NO cabe
        Proceso("P5", 4, 3, 50),
        Proceso("P6", 5, 6, 100),  # Entrará cuando libere alguna
    ]

    # --- ARRIBOS ---
    for p in procesos:
        ok, motivo = gm.intentar_admitir(p)
        evento = f"ARRIBO {p.id} (mem={p.memoria_requerida}K) -> {'Listo' if ok else 'Listo/Suspendido'} [{motivo}]"
        imprimir_tabla(gm.snapshot_tabla_memoria(), evento)

    # ¿Quiénes quedaron esperando memoria?
    en_espera = [p.id for p in gm.espera_memoria]
    if en_espera:
        print("\nProcesos en espera por memoria:", en_espera)
    else:
        print("\nNo hay procesos en espera por memoria.")

    # --- FIN de un proceso para liberar y probar admisión en cascada ---
    # Elegimos liberar P2 (si fue admitido). Si P2 no entró, liberamos el que haya caído en 250 o 150.
    candidato = None
    for part in gm.particiones:
        if not part.reservada and not part.libre and part.proceso and part.proceso.id == "P2":
            candidato = part.proceso
            break
    if not candidato:
        # fallback: liberar el primero no reservado y ocupado
        for part in gm.particiones:
            if not part.reservada and not part.libre and part.proceso:
                candidato = part.proceso
                break

    if candidato:
        gm.liberar_proceso(candidato)
        imprimir_tabla(gm.snapshot_tabla_memoria(), f"FIN_CPU {candidato.id} -> libera partición; reintentos FIFO+Best-Fit")
    else:
        print("\nNo se encontró proceso para liberar (revisar datos de prueba).")

    # Resultado final: mostrar estado y quiénes (si quedan) siguen esperando
    en_espera = [p.id for p in gm.espera_memoria]
    if en_espera:
        print("\nAún en espera por memoria:", en_espera)
    else:
        print("\nSin procesos en espera. OK.")

if __name__ == "__main__":
    main()
