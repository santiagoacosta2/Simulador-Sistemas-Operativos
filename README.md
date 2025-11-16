# Simulador de Sistemas Operativos – UTN ISI 2025

### Particiones fijas + Best-Fit + SRTF con desalojo

Este proyecto implementa un simulador completo de un Sistema Operativo académico, siguiendo la consigna del TPI (Trabajo Práctico Integrador) de la cátedra Sistemas Operativos – UTN ISI.

El simulador integra **gestión de memoria**, **planificación de CPU**, **métricas**, **trazabilidad paso a paso** y un **modo de presentación interactiva**.

---

## Características principales

### 1. Gestión de memoria

- Esquema de **particiones fijas**:

  - SO: 100 KB
  - U1: 250 KB
  - U2: 150 KB
  - U3: 50 KB

- Política de asignación: **Best-Fit**.
- Control de **grado de multiprogramación = 5**.
- **Cola de espera FIFO** para procesos que no pueden entrar en memoria.
- Manejo explícito del caso **“NO_CABE_EN_NINGUNA”** (proceso descartado sin romper la simulación).

---

### 2. Planificación de CPU: SRTF con desalojo

- Implementada como un **Scheduler independiente**.
- Mantiene:

  - Proceso en CPU
  - Cola de listos ordenada por _tiempo restante_ (heapq)

- Si llega un proceso más corto → **desalojo inmediato**.

---

### 3. Simulación completa

- Eventos: **ARRIBO** y **FIN_CPU**
- Avance de reloj por “salto al próximo evento”.
- Coordinación total CPU ↔ Memoria.
- Snapshots detallados con:

  - CPU + tiempo restante
  - Cola de listos (SRTF)
  - Tabla completa de memoria
  - Cola de espera de memoria

Ejecutar:

```bash
python main.py --csv procesos.csv --verbose
```

---

### 4. Métricas finales del sistema

Por proceso:

- Tiempo de retorno
- Tiempo de espera
- Tiempo de respuesta
- Tiempo de fin e inicio

Globales:

- Promedio de retorno
- Promedio de espera
- Promedio de respuesta
- Throughput

---

### 5. Modo presentación (para defensa)

Incluye un script interactivo:

```bash
python presentacion.py
```

El menú permite:

- Ver arquitectura
- Ver código de cada módulo con numeración de líneas
- Ejecutar una simulación demo
- Mostrar los puntos fuertes del diseño

Ideal para la defensa del TPI.

---

## Estructura del proyecto

```text
Simulador-Sistemas-Operativos/
│
├── procesos.py              # Modelo Proceso
├── memoria.py               # Particiones fijas + Best-Fit
├── planificador_srtf.py     # Scheduler SRTF con desalojo
├── simulacion.py            # Orquestador del sistema
├── io_metricas.py           # CSV + utilidades
├── main.py                  # Entrada principal de ejecución
├── presentacion.py          # Interfaz de presentación
├── procesos.csv             # Ejemplo de entrada
├── README.md                # Este archivo
└── requirements.txt         # Dependencias
```

---

## Ejecución rápida

1. Instalación (opcional):

```bash
pip install -r requirements.txt
```

2. Ejecutar simulación:

```bash
python main.py --csv procesos.csv --verbose
```

3. Ejecutar presentación:

```bash
python presentacion.py
```

---

## Requisitos del TPI cumplidos

El simulador cumple **todas** las especificaciones del TPI:

- Particiones fijas correctas
- Best-Fit
- Cola de espera memoria FIFO
- SRTF con desalojo
- Manejo del caso “no cabe en ninguna partición”
- Snapshots completos en cada evento
- Métricas finales
- Manejo de hasta 10 procesos
- Código modular, limpio y extensible

---

## Extensiones posibles

- Múltiples esquemas de memoria (dinámica, Buddy, Paginación)
- Otros algoritmos de CPU (RR, MFQ, FIFO, HRRN)
- Visualización gráfica con pygame o Tkinter
- Formatos de salida HTML/JSON para comparar corridas

---

# Borrador de Informe – Simulador de Sistemas Operativos

## 1. Introducción

El objetivo del presente trabajo es desarrollar un simulador de un Sistema Operativo académico capaz de integrar dos componentes fundamentales:

1. **Gestión de memoria mediante particiones fijas y política Best-Fit.**
2. **Planificación de CPU con el algoritmo SRTF (Shortest Remaining Time First) con desalojo.**

El simulador debe coordinar ambos subsistemas, gestionar eventos de arribo y finalización de CPU, avanzar el reloj por saltos y producir métricas de rendimiento del sistema.

El desarrollo se realizó siguiendo principios de modularización, claridad, mantenibilidad y trazabilidad paso a paso.

---

## 2. Arquitectura general del sistema

El sistema se implementó con una **arquitectura modular**, donde cada archivo Python representa un componente claramente separado.

### 2.1 Módulos del proyecto

- `procesos.py`: define la clase `Proceso`, que representa un proceso del sistema (ID, tiempo de arribo, ráfaga de CPU, memoria requerida, tiempo restante).
- `memoria.py`: implementa la gestión de memoria con particiones fijas, política Best-Fit, grado de multiprogramación y cola de espera de procesos.
- `planificador_srtf.py`: contiene el planificador de CPU, implementando el algoritmo SRTF con desalojo sobre una estructura de heap.
- `simulacion.py`: es el orquestador de la simulación; coordina eventos, reloj, interacción entre memoria y CPU, y calcula métricas finales.
- `io_metricas.py`: se encarga de la carga de procesos desde un archivo CSV, validación de datos y utilidades de impresión.
- `main.py`: actúa como punto de entrada del simulador, expone una interfaz de línea de comandos y arma los componentes.
- `presentacion.py`: provee un modo de presentación interactiva para mostrar la arquitectura, el código y una demo de ejecución.

### 2.2 Diseño orientado a responsabilidades

Se adoptó un diseño en capas lógicas:

- **Capa de dominio**: definición de `Proceso`.
- **Capa de servicios de infraestructura**: gestor de memoria y planificador de CPU.
- **Capa de orquestación**: simulador y ciclo de eventos.
- **Capa de interfaz**: `main.py` para CLI y `presentacion.py` para la defensa.

Este enfoque permite reemplazar o extender componentes (por ejemplo, otro algoritmo de planificación o otro esquema de memoria) sin reescribir la lógica de simulación.

---

## 3. Modelo de Proceso

Cada proceso posee la siguiente información relevante:

- **ID**: identificador simbólico (por ejemplo, P1, P2, P3, ...).
- **Tiempo de arribo**: instante en el que el proceso llega al sistema.
- **Ráfaga de CPU**: cantidad total de unidades de tiempo que el proceso necesita de CPU.
- **Memoria requerida**: tamaño en KB que el proceso necesita en memoria principal.
- **Tiempo restante de CPU**: se inicializa con la ráfaga total y se va decrementando durante la simulación.
- **Tiempos para métricas**: se almacenan tiempos de inicio de CPU, fin, retorno, espera y respuesta.

El modelo está pensado para calcular de forma directa todas las métricas de planificación y de servicio que exige la consigna.

---

## 4. Gestión de Memoria

### 4.1 Particiones fijas

El espacio de memoria principal se modela mediante particiones fijas:

- Partición de SO: 100 KB.
- Partición de usuario U1: 250 KB.
- Partición de usuario U2: 150 KB.
- Partición de usuario U3: 50 KB.

La partición de SO se reserva permanentemente y las particiones de usuario se utilizan para la asignación de procesos.

### 4.2 Política Best-Fit

Cuando un proceso solicita memoria, se aplica la política **Best-Fit** sobre las particiones de usuario:

1. Se descartan las particiones donde el proceso no cabe (tamaño del proceso mayor al tamaño de la partición).
2. Entre las particiones viables, se elige aquella donde la fragmentación interna sea mínima.
3. Si existe una partición libre adecuada, el proceso se carga allí y aumenta el grado de multiprogramación.
4. Si no hay particiones libres pero el proceso podría entrar cuando se libere alguna, se encola en la **cola de espera de memoria**.
5. Si el proceso no cabe en ninguna partición del sistema (ni siquiera en la más grande), se marca como **descartado**.

### 4.3 Grado de multiprogramación y cola de espera

El simulador controla un **grado de multiprogramación máximo de 5 procesos** en memoria de usuario.

- Cuando se alcanza este límite, los nuevos procesos que llegan se encolan en la **cola de espera de memoria**.
- Cuando un proceso finaliza y libera una partición, el gestor de memoria recorre la cola de espera en orden FIFO e intenta admitir los procesos pendientes.

Este esquema respeta la consigna del TPI y permite analizar el impacto de la multiprogramación en los tiempos de espera.

---

## 5. Planificación de CPU

### 5.1 Algoritmo SRTF con desalojo

El algoritmo de planificación elegido es **SRTF (Shortest Remaining Time First)**, en su variante **preemptive** (con desalojo):

- En cada instante, el proceso que ocupa la CPU es aquel con menor **tiempo de CPU restante**.
- Si arriba un proceso nuevo con un tiempo restante menor que el del proceso actual, se produce un **desalojo**: el proceso en CPU pasa a la cola de listos y el nuevo proceso entra a CPU.

### 5.2 Implementación del Scheduler

El Scheduler se implementa como un componente independiente (`SrtfScheduler`) que mantiene:

- Un puntero al proceso actual en CPU.
- Una cola de listos basada en un `heap` (estructura de datos de prioridad).

Las operaciones principales son:

- `agregar_proceso(proceso, tiempo_actual)`: registra el proceso. Decide si entra directamente a CPU o si va a la cola de listos, y realiza el desalojo si corresponde.
- `avanzar_tiempo(delta)`: descuenta CPU del proceso actual, reduciendo su tiempo restante.
- `sacar_proceso_actual()`: se invoca al detectar un evento FIN_CPU; extrae el proceso que termina y selecciona el siguiente de la cola de listos.
- `hay_listos() / proceso_en_cpu()`: exponen el estado del scheduler al simulador.

Esta implementación permite cambiar el algoritmo de planificación sin modificar `simulacion.py`.

---

## 6. Ciclo de Simulación

La simulación avanza en el tiempo procesando dos tipos de eventos:

- **ARRIBO** de un proceso.
- **FIN_CPU** del proceso que está en ejecución.

### 6.1 Evento ARRIBO

Cuando el reloj alcanza el tiempo de arribo de uno o más procesos:

1. Se toma cada proceso cuyo arribo coincide con el tiempo actual.
2. Se intenta admitir en memoria aplicando la política Best-Fit.
3. Si el proceso queda asignado a una partición:

   - Se inicializa su tiempo restante de CPU, si no estaba inicializado.
   - Se pasa al Scheduler SRTF.
   - Si ingresa directamente a CPU por primera vez, se registra el **tiempo de inicio de CPU**.

4. Si no puede ser admitido pero **podría caber en alguna partición futura**, se lo encola en la cola de espera de memoria.
5. Si no cabe en ninguna partición del sistema, se lo marca como **descartado**.

### 6.2 Evento FIN_CPU

Un evento FIN_CPU ocurre cuando el tiempo restante del proceso en CPU llega a cero:

1. El proceso se marca como terminado y se registra su **tiempo de fin**.
2. Se libera la partición de memoria ocupada por ese proceso.
3. El gestor de memoria recorre la cola de espera y reintenta admitir procesos pendientes.
4. Los procesos que logran entrar a memoria se envían al Scheduler SRTF.
5. El Scheduler selecciona el próximo proceso a ejecutar, respetando la política de menor tiempo restante.

### 6.3 Avance de reloj

El reloj avanza **por saltos** hacia el próximo evento relevante:

- Se calcula el tiempo del próximo arribo.
- Se calcula el tiempo estimado del próximo FIN_CPU.
- El reloj salta al menor de ambos tiempos.
- En caso de empate, se resuelve primero el FIN_CPU.

Este enfoque hace eficiente la simulación y evita avanzar el reloj paso a paso innecesariamente.

---

## 7. Snapshots del estado del sistema

Para facilitar el análisis y la defensa del trabajo, el simulador ofrece un modo **verbose**, donde en cada evento se imprime un snapshot del estado global:

- Tiempo actual `t`.
- Tipo de evento (ARRIBO o FIN_CPU).
- Proceso en CPU y su tiempo restante.
- Cola de listos del Scheduler SRTF, detallando procesos y tiempos restantes.
- Tabla completa de memoria con:

  - Partición.
  - Base.
  - Tamaño.
  - Proceso asignado.
  - Memoria ocupada.
  - Fragmentación interna.

- Cola de espera de memoria con la lista de procesos en espera.

Esto provee trazabilidad completa del comportamiento del sistema.

---

## 8. Métricas finales

Al finalizar la simulación, se calculan las métricas por proceso y globales.

### 8.1 Métricas por proceso

Para cada proceso **que terminó su ejecución**:

- **Tiempo de retorno**: `t_fin - t_arribo`.
- **Tiempo de espera**: `tiempo_retorno - ráfaga_CPU`.
- **Tiempo de respuesta**: `t_inicio_cpu - t_arribo`.

Los procesos que fueron descartados por no caber en ninguna partición no se incluyen en las métricas.

### 8.2 Métricas globales

Se calculan:

- **Promedio de tiempo de retorno**.
- **Promedio de tiempo de espera**.
- **Promedio de tiempo de respuesta**.
- **Throughput**: cantidad de procesos completados dividido el tiempo total simulado.

Estas métricas permiten evaluar el desempeño de la combinación de políticas de memoria y planificación elegida.

---

## 9. Conclusiones

El simulador diseñado cumple con todas las especificaciones planteadas en la consigna del TPI:

- Gestión de memoria con particiones fijas y política Best-Fit.
- Control explícito del grado de multiprogramación y cola de espera de memoria.
- Implementación del algoritmo de planificación SRTF con desalojo.
- Simulación basada en eventos con avance de reloj por saltos.
- Snapshots detallados que permiten analizar paso a paso el comportamiento del sistema.
- Cálculo de métricas por proceso y globales.

Además, el diseño modular facilita la extensión futura del trabajo, ya sea para incorporar nuevos algoritmos de planificación o nuevos esquemas de gestión de memoria.


