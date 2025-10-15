# test_memoria.py
# -----------------------------------------------------------
# Demo + test de la memoria de la consigna:
# Particiones fijas:
#   - SO: 100K reservada
#   - Usuario: 250K, 150K, 50K
# Política: Best-Fit + grado de multiprogramación (por defecto 5).
#
# Modo script: imprime tabla en cada evento.
# Modo pytest: ejecuta las mismas acciones y valida estados con asserts.
# -----------------------------------------------------------

from memoria import GestorMemoria
from procesos import Proceso


# -------- impresión simple en texto (no depende de io_metricas) --------
def _imprimir_tabla(filas, titulo=""):
    if titulo:
        print(f"\n=== {titulo} ===")
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
    for f in filas:
        print(
            f"{f['Partición']:>9} | {f['Dirección']:>9} | {f['Tamaño']:>6} | {f['Proceso']:>12} | {f['Frag. interna']:>14}"
        )


# ----------------------- escenario común -----------------------
def _escenario(gm: GestorMemoria, imprimir: bool = True):
    """
    Crea los procesos del enunciado y ejecuta:
      - Arribos en orden
      - FIN de P2 (si está en memoria) o del primero de usuario que esté ocupado
    Retorna (espera_antes, candidato_fin, espera_despues)
    """
    procesos = [
        Proceso("P1", 0, 8, 90),
        Proceso("P2", 1, 5, 240),
        Proceso("P3", 2, 4, 80),
        Proceso("P4", 3, 7, 300),  # NO cabe en ninguna
        Proceso("P5", 4, 3, 50),
        Proceso("P6", 5, 6, 100),  # Entrará tras liberar alguna
    ]

    # ARRIBOS
    for p in procesos:
        ok, motivo = gm.intentar_admitir(p)
        if imprimir:
            evento = f"ARRIBO {p.id} (mem={p.memoria_requerida}K) -> {'Listo' if ok else 'Listo/Suspendido'} [{motivo}]"
            _imprimir_tabla(gm.snapshot_tabla_memoria(), evento)

    espera_antes = [p.id for p in gm.espera_memoria]

    # Elegir P2 si está en memoria, si no cualquiera de usuario
    candidato = None
    for part in gm.particiones:
        if (
            not part.reservada
            and not part.libre
            and part.proceso
            and part.proceso.id == "P2"
        ):
            candidato = part.proceso
            break
    if not candidato:
        for part in gm.particiones:
            if not part.reservada and not part.libre and part.proceso:
                candidato = part.proceso
                break

    if candidato:
        gm.liberar_proceso(candidato)
        if imprimir:
            _imprimir_tabla(
                gm.snapshot_tabla_memoria(),
                f"FIN_CPU {candidato.id} -> libera partición; reintentos FIFO+Best-Fit",
            )
    elif imprimir:
        print("\nNo se encontró proceso para liberar (revisar datos de prueba).")

    espera_despues = [p.id for p in gm.espera_memoria]
    return espera_antes, (candidato.id if candidato else None), espera_despues


# ----------------------- modo pytest -----------------------
def test_memoria_consigna_flujo_basico():
    gm = GestorMemoria()  # mapa por defecto: SO(100) + 250 + 150 + 50

    espera_antes, candidato, espera_despues = _escenario(gm, imprimir=False)

    # Después de todos los arribos:
    # - P3 espera porque 150 y 50 están ocupadas/insuficientes en ese instante.
    # - P4 no cabe en ninguna.
    # - P6 espera porque no hay partición libre adecuada en ese momento.
    assert espera_antes == ["P3", "P4", "P6"]

    # Debe haberse elegido P2 para liberar si estaba en memoria.
    assert candidato in {"P2", "P1", "P5"}  # fallback posible si el dataset cambia

    # Tras liberar la de 250K, P3 entra por reintento FIFO+Best-Fit.
    # Siguen esperando P4 (no cabe) y P6.
    assert espera_despues == ["P4", "P6"]


# ----------------------- modo script -----------------------
def main():
    gm = GestorMemoria()
    espera_antes, candidato, espera_despues = _escenario(gm, imprimir=True)

    if espera_antes:
        print("\nProcesos en espera por memoria:", espera_antes)
    else:
        print("\nNo hay procesos en espera por memoria.")

    if candidato:
        print(f"\nSe liberó: {candidato}")
    else:
        print("\nNo se liberó ningún proceso.")

    if espera_despues:
        print("\nAún en espera por memoria:", espera_despues)
    else:
        print("\nSin procesos en espera. OK.")


if __name__ == "__main__":
    main()
