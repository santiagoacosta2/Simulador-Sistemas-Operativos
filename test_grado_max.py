from memoria import GestorMemoria
from procesos import Proceso


def test_grado_max():
    mem = GestorMemoria()  # usa particiones por defecto (SO+250+150+50)
    ps = [Proceso(f"P{i}", i, 5, 60) for i in range(6)]
    admitidos = 0
    for p in ps:
        ok, _ = mem.intentar_admitir(p)
        if ok:
            admitidos += 1
    assert admitidos <= 5
