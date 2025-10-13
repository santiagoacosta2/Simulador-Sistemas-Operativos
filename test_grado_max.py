# test_grado_max.py
from procesos import Proceso
from memoria import GestorMemoria

gm = GestorMemoria()  # 3 particiones de usuario (250,150,50) + SO

# 6 procesos que SI caben (salvo que se llenen particiones):
ps = [
    Proceso(f"P{i}", 0, 5, 50) for i in range(1, 7)
]

for p in ps:
    ok, motivo = gm.intentar_admitir(p)
    print(f"{p.id}: {'Listo' if ok else 'Listo/Suspendido'} [{motivo}]")

print("\nEn memoria:", sum(1 for p in gm.particiones if not p.reservada and not p.libre))
print("En espera:", [p.id for p in gm.espera_memoria])
