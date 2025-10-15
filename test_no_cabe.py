# test_no_cabe.py
# -----------------------------------------------------------
# Verifica rechazo inmediato cuando el proceso requiere
# más memoria que la mayor partición de usuario.
# Debe quedar en espera con motivo "no_cabe_en_ninguna".
# -----------------------------------------------------------

from memoria import GestorMemoria
from procesos import Proceso


def test_no_cabe():
    gm = GestorMemoria()  # SO=100K reservada; usuario: 250K, 150K, 50K
    grande = Proceso(id="PX", t_arribo=0, duracion_cpu=5, memoria_requerida=9999)

    ok, motivo = gm.intentar_admitir(grande)

    # Rechazo por tamaño
    assert ok is False and motivo == "no_cabe_en_ninguna"
    # Queda en la cola de espera
    assert [p.id for p in gm.espera_memoria] == ["PX"]
    # Estado coherente
    assert grande.particion_asignada is None and grande.estado == "Listo/Suspendido"
