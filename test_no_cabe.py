from procesos import Proceso
from memoria import GestorMemoria


def test_no_cabe():
    gm = GestorMemoria()
    grande = Proceso("PX", 0, 5, 9999)
    ok, motivo = gm.intentar_admitir(grande)
    assert not ok and motivo == "no_cabe_en_ninguna"
