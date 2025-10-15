# Simulador de Sistemas Operativos — Entrega 1

## Objetivo

Simular arribos de procesos y gestión de memoria con particiones fijas. Mostrar snapshots de memoria y flujo básico de eventos. El proyecto queda preparado para integrar planificación SRTF con desalojo y métricas finales.

## Requisitos

- Windows 11.
- Python 3.13 en venv `.venv`.
- Dependencias: `prettytable`, `pytest`, `black`, `ruff`.

## Instalación

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Herramientas de desarrollo (si no están en requirements)
python -m pip install pytest black ruff
```

## Ejecución

```powershell
# Modo silencioso (sin snapshots)
python main.py --csv procesos.csv

# Modo verbose (con snapshots de memoria y eventos)
python main.py --csv procesos.csv --verbose
```

## Formato del CSV

Cabecera y columnas:

```
ID,Arribo,RafagaCPU,Memoria
```

Ejemplo:

```
P1,0,8,90
P2,1,5,240
P3,2,3,80
P4,3,7,300
P5,4,2,50
P6,5,4,100
```

Reglas de validación actuales (mínimas):

- `Arribo >= 0`
- `RafagaCPU > 0`
- `Memoria > 0`

## Funcionalidad implementada

- **Memoria**: particiones fijas

  - SO: 100K reservada.
  - Usuario: 250K, 150K, 50K.
  - Asignación **Best-Fit**.
  - **Grado de multiprogramación = 5**.
  - Cola de espera por memoria y reintentos FIFO al liberar.
  - Snapshot tabular con fragmentación interna.

- **Eventos**

  - **ARRIBO**: intenta admitir y encola en ready si entra.
  - **FIN_CPU** (demo): libera y dispara reintentos de espera.

- **CLI**

  - `--csv` para ruta del archivo de procesos.
  - `--verbose` para imprimir eventos y snapshots.

- **Pruebas**

  - `pytest` con 3 tests: límite de grado, proceso que no cabe y flujo de memoria.
  - `black` y `ruff` en verde.

## Arquitectura del código

- `procesos.py`: `Proceso`, `Particion`.
- `memoria.py`: `GestorMemoria` con Best-Fit, grado, espera y reintentos.
- `planificador.py`: cola SRTF (lista para integrar con CPU).
- `simulacion.py`: lectura CSV, ARRIBO, FIN de demo, control `--verbose`.
- `io_metricas.py`: carga de CSV, logging, snapshot y resumen simple de métricas.
- `main.py`: CLI y arranque del simulador.

## Flujo de trabajo con Git

- Rama principal: `main`.
- Rama de desarrollo sugerida: `feature/entrega1` → PR a `main`.
- Comandos útiles:

```powershell
black .; ruff check .; pytest -q
git add -A
git commit -m "mensaje"
git push
```

## Limitaciones y trabajo pendiente

- Integrar planificación **SRTF** con desalojo en el ciclo de CPU.
- Política explícita **ARRIBO vs FIN_CPU** en el mismo tiempo (priorizar FIN_CPU).
- Métricas completas por proceso: `t_final`, turnaround, espera; promedios y throughput.
- Test de **preempción SRTF**.
- Validación estricta de CSV y ejemplos extendidos en README.

## Ejemplo de salida (modo verbose)

```
[t=0] ARRIBO P1 (mem=90K) -> Listo [asignado_p2]
=== Snapshot Memoria ===
Partición | Dirección | Tamaño | Proceso | Frag. interna
...
```
