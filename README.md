# Simulador de Sistemas Operativos — Entrega 1 (estado actual)

## Objetivo

Simular arribos de procesos y gestión de memoria con particiones fijas. Mostrar snapshots de memoria y flujo básico de eventos. Preparado para incorporar planificación SRTF con desalojo y métricas finales.

## Requisitos

- Windows 11.
- Python 3.13 en venv `.venv`.
- Dependencias: `prettytable`, `pytest`, `black`, `ruff`.

## Instalación

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest black ruff
```

## Ejecución

```powershell
# silencioso (sin snapshots)
python main.py --csv procesos.csv

# verbose (con snapshots de memoria y eventos)
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
  - **Grado multiprogramación = 5**.
  - Cola de espera por memoria y reintentos FIFO al liberar.
  - Snapshot tabular con fragmentación interna.

- **Eventos**:

  - ARRIBO: intenta admitir y encola en ready si entra.
  - FIN_CPU (demo): libera y dispara reintentos de espera.

- **CLI**:

  - `--csv` para ruta del archivo de procesos.
  - `--verbose` para imprimir eventos y snapshots.

- **Pruebas**:

  - `pytest` con 2 tests: límite de grado y proceso que no cabe.
  - `black` y `ruff` sin errores.

## Arquitectura del código

- `procesos.py`: `Proceso`, `Particion`.
- `memoria.py`: `GestorMemoria` con Best-Fit, grado, espera y reintentos.
- `planificador.py`: cola SRTF (lista para integrar con CPU).
- `simulacion.py`: lectura CSV, ARRIBO, FIN de demo, control `--verbose`.
- `io_metricas.py`: carga de CSV, logging y snapshot de memoria.
- `main.py`: CLI y arranque del simulador.

## Uso de Git

- Rama de trabajo: `feature/entrega1`.
- Estándar:

  ```powershell
  black .; ruff check .; pytest -q
  git add -A
  git commit -m "mensaje"
  git push
  ```

## Limitaciones y trabajo pendiente

- Planificación **SRTF** con desalojo integrada al ciclo de CPU.
- Política explícita de empate `ARRIBO == FIN_CPU` (priorizar FIN_CPU) en el loop principal.
- **Métricas finales**: `t_final`, turnaround y espera por proceso, promedios y throughput.
- Test adicional de **preempción SRTF**.
- Mensajes de validación estricta del CSV y README con ejemplos ampliados.

## Ejemplo de salida (modo verbose)

```
[t=0] ARRIBO P1 (mem=90K) -> Listo [asignado_p2]
=== Snapshot Memoria ===
Partición | Dirección | Tamaño | Proceso | Frag. interna
...
```

## Contacto y contribución

- Abrir PR en modo **Draft** desde `feature/entrega1` hacia `main`.
- No mergear a `main` hasta completar métricas y SRTF.
