# test_grado_max.py
# -----------------------------------------------------------
# Verifica que el límite de grado de multiprogramación se cumple.
# Crea un mapa de memoria donde *sí* caben 6 procesos de 60K,
# pero fija grado_max=5 para forzar que el 6º quede en espera
# por "grado_max" y no por tamaño.
# -----------------------------------------------------------

from memoria import GestorMemoria
from procesos import Particion, Proceso


def test_grado_max():
    # Mapa de particiones:
    # - SO 100K reservada (ya ocupada)
    # - 5 particiones de usuario de 100K (todas libres)
    parts = [
        Particion(id_particion=0, base=0, tamaño=100, reservada=True, libre=False),
        Particion(id_particion=1, base=100, tamaño=100),
        Particion(id_particion=2, base=200, tamaño=100),
        Particion(id_particion=3, base=300, tamaño=100),
        Particion(id_particion=4, base=400, tamaño=100),
        Particion(id_particion=5, base=500, tamaño=100),
    ]

    # Grado de multiprogramación = 5
    mem = GestorMemoria(particiones=parts, grado_max=5)

    # 6 procesos que entran por tamaño (60K) pero el 6º debe quedar fuera por grado
    procesos = [
        Proceso(f"P{i}", t_arribo=i, duracion_cpu=5, memoria_requerida=60)
        for i in range(1, 7)
    ]

    admitidos = 0
    ultimo_ok = None
    ultimo_motivo = None

    for p in procesos:
        ok, motivo = mem.intentar_admitir(p)
        ultimo_ok, ultimo_motivo = ok, motivo
        if ok:
            admitidos += 1

    # Se admiten exactamente 5
    assert admitidos == 5
    # El 6º quedó fuera por límite de grado, no por tamaño
    assert ultimo_ok is False and ultimo_motivo == "grado_max"
    # La cola de espera debe contener 1 proceso
    assert len(mem.espera_memoria) == 1
    assert mem.espera_memoria[0].id == "P6"
