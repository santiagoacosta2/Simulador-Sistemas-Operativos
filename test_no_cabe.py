# test_no_cabe.py
from procesos import Proceso
from memoria import GestorMemoria

gm = GestorMemoria()
grande = Proceso("PX", 0, 5, 9999)  # imposible

ok, motivo = gm.intentar_admitir(grande)
print(f"PX: {'Listo' if ok else 'Listo/Suspendido'} [{motivo}]")
print("En espera:", [p.id for p in gm.espera_memoria])
