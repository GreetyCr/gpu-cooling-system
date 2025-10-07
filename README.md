# Sistema de Enfriamiento Líquido para GPU

Simulación numérica de transferencia de calor transitoria en un sistema de enfriamiento líquido para GPU mediante métodos de diferencias finitas.

## 📋 Descripción del Proyecto

Este proyecto simula el comportamiento térmico de un sistema de enfriamiento líquido para GPU compuesto por:
- **Placa base rectangular** con aletas semicirculares de expansión de superficie
- **3 aletas semicirculares** (domos) en la parte superior
- **Canal de agua** en la parte inferior con flujo en dirección axial
- **Convección con aire ambiente** en las superficies superiores

### Objetivo

Calcular el tiempo que tarda el sistema en llegar al estado estacionario después de un cambio en la temperatura del agua (de 50 °C a 80 °C), comparando dos materiales:
- **Aluminio 6061**
- **Acero Inoxidable 304**

## 🏗️ Estructura del Proyecto

```
python-adrian/
├── main.py                   # 🚀 Script principal (CLI + menú interactivo)
├── interfaz_web.py           # 🌐 Interfaz web con Streamlit
├── requirements.txt          # 📦 Dependencias del proyecto
├── README.md                 # 📖 Este archivo
│
├── src/                      # 💻 Código fuente principal
│   ├── parametros.py         # Parámetros físicos y numéricos
│   ├── mallas.py             # Generación de mallas
│   ├── fluido.py             # Solver 1D del fluido
│   ├── placa.py              # Solver 2D de la placa
│   ├── aletas.py             # Solver 2D cilíndrico de aletas
│   ├── acoplamiento.py       # Acoplamiento entre dominios
│   ├── solucionador.py       # Bucle temporal maestro
│   └── visualizacion.py      # Funciones de graficación
│
├── contexto/                 # 📚 Documentación técnica del problema
│   ├── 00_guia_implementacion.md
│   ├── 01_contexto_proyecto.md
│   ├── 02_parametros_sistema.md
│   ├── 03_ecuaciones_gobernantes.md
│   ├── 04_condiciones_frontera.md
│   ├── 05_discretizacion_numerica.md
│   └── 06_herramientas_desarrollo.md
│
├── docs/                     # 📝 Documentación adicional
│   ├── PLAN_ORGANIZACION.md  # Plan de organización del repo
│   ├── adr/                  # Architecture Decision Records
│   ├── analisis/             # 📊 Análisis e informes
│   │   ├── ANALISIS_INGENIERIL_RESULTADOS.md
│   │   ├── ENTREGABLES_PRESENTACION.md
│   │   └── codigo_resumen_presentacion.py
│   ├── guias/                # 📘 Guías de uso
│   │   ├── INSTRUCCIONES_USO.txt
│   │   ├── COMANDOS_STREAMLIT.txt
│   │   └── README_INTERFAZ.md
│   └── notas/                # 📋 Notas de desarrollo
│       ├── ACTUALIZACION_PROGRESO.md
│       ├── CORRECCION_ATRIBUTOS.md
│       ├── DISTRIBUCION_ESPACIAL.md
│       ├── RESUMEN_CONVERGENCIA.md
│       ├── TEST_MAIN.md
│       └── INSTRUCCIONES_VISUALIZACIONES_SS.md
│
├── scripts/                  # 🔧 Scripts auxiliares
│   ├── simulacion/           # Scripts de simulación
│   │   ├── simular_acero.py
│   │   └── generar_grafico_convergencia.py
│   ├── visualizacion/        # Scripts de visualización
│   │   ├── generar_grafico_rapido.py
│   │   ├── generar_visualizaciones_SS.py
│   │   └── ejemplo_distribucion_espacial.py
│   └── utilidades/           # Scripts de monitoreo
│       ├── monitorear_convergencia.sh
│       └── monitorear_simulacion_SS.sh
│
├── logs/                     # 📋 Logs de ejecución y desarrollo
│   ├── worklog.md            # 📝 Registro completo de desarrollo
│   ├── convergencia_output.log
│   ├── simulacion_SS.log
│   └── simulacion_log.txt
│
├── resultados/               # 📊 Resultados de simulaciones
│   ├── datos/                # Archivos .npz generados
│   └── figuras/              # Gráficos y visualizaciones
│
├── tests/                    # ✅ Tests unitarios y de integración
└── todo/                     # 📌 Tareas pendientes
    └── instrucciones_ecuaciones.md
```

## ⚡ Accesos Rápidos

### 🎯 Puntos de Entrada Principales

| Archivo | Descripción | Comando |
|---------|-------------|---------|
| `main.py` | Script principal con CLI y menú interactivo | `python3 main.py` |
| `interfaz_web.py` | Interfaz web con Streamlit | `streamlit run interfaz_web.py` |

### 📂 Archivos Importantes

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| **Análisis de Resultados** | `docs/analisis/ANALISIS_INGENIERIL_RESULTADOS.md` | Interpretación completa de resultados Al vs SS |
| **Código para Presentación** | `docs/analisis/codigo_resumen_presentacion.py` | Ecuaciones implementadas (ejecutable) |
| **Guía de Entregables** | `docs/analisis/ENTREGABLES_PRESENTACION.md` | Estructura de presentación |
| **Instrucciones de Uso** | `docs/guias/INSTRUCCIONES_USO.txt` | Guía completa (Terminal, Jupyter, Spyder) |
| **Interfaz Web** | `docs/guias/README_INTERFAZ.md` | Guía de la interfaz Streamlit |
| **Worklog Completo** | `logs/worklog.md` | Registro detallado de desarrollo |
| **Plan de Organización** | `docs/PLAN_ORGANIZACION.md` | Estructura del repositorio |

### 🔧 Scripts Útiles

| Script | Ubicación | Propósito |
|--------|-----------|-----------|
| `simular_acero.py` | `scripts/simulacion/` | Simulación específica para Acero Inoxidable |
| `generar_visualizaciones_SS.py` | `scripts/visualizacion/` | Generar todas las figuras de SS |
| `ejemplo_distribucion_espacial.py` | `scripts/visualizacion/` | Ejemplo de distribución espacial completa |
| `monitorear_simulacion_SS.sh` | `scripts/utilidades/` | Monitor de progreso en tiempo real |

### 📊 Resultados Disponibles

- **Datos**: `resultados/datos/*.npz` - Archivos binarios con temperaturas vs tiempo
- **Figuras**: `resultados/figuras/*.png` - Gráficos generados (18 figuras: 9 Al + 9 SS)

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone https://github.com/GreetyCr/gpu-cooling-system.git
cd gpu-cooling-system

# Instalar dependencias
pip install -r requirements.txt
```

## 📦 Dependencias Principales

- **numpy** >= 1.24.0 - Operaciones numéricas y arrays
- **scipy** >= 1.10.0 - Algoritmos científicos avanzados
- **matplotlib** >= 3.7.0 - Visualización de resultados
- **pandas** >= 2.0.0 - Manejo de datos tabulares
- **numba** >= 0.57.0 - Aceleración JIT de bucles numéricos
- **seaborn** >= 0.12.0 - Visualizaciones estadísticas
- **tqdm** >= 4.65.0 - Barras de progreso

## 🧮 Métodos Numéricos

El proyecto implementa:

- **Diferencias finitas explícitas** para ecuaciones de conducción de calor
- **Método de volúmenes finitos** para el flujo 1D del agua
- **Esquema FTCS** (Forward Time, Central Space) para discretización temporal
- **Acoplamiento térmico** mediante interpolación y continuidad de flujos
- **Condiciones de estabilidad**: CFL < 1, Fourier < 0.5

## 📐 Modelo Físico

### Dominios de Simulación

1. **Fluido (agua)**: Modelo 1D convectivo en dirección x
2. **Placa base**: Modelo 2D cartesiano (x-y)
3. **Aletas semicirculares**: Modelo 2D cilíndrico (r-θ)

### Suposiciones Principales

- Problema 2D (sin variación en dirección z)
- Propiedades termofísicas constantes
- Coeficientes convectivos constantes (h_agua = 600 W/m²K, h_aire = 10 W/m²K)
- Contacto térmico perfecto en interfaces
- Sin radiación térmica
- Sin generación de calor interna

## 🎯 Uso

### Modo 1: Script Principal (Recomendado)

```bash
# Menú interactivo
python3 main.py

# Simulación rápida (5 segundos)
python3 main.py --rapido

# Simulación completa (hasta convergencia)
python3 main.py --completo

# Solo generar visualizaciones de resultados existentes
python3 main.py --solo-visualizacion

# Comparar ambos materiales
python3 main.py --comparar

# Ver todas las opciones
python3 main.py --help
```

### Modo 2: Interfaz Web

```bash
streamlit run interfaz_web.py
```

Luego abre tu navegador en `http://localhost:8501`

### Modo 3: Programático (Python)

```python
from src.parametros import Parametros
from src.mallas import generar_todas_mallas
from src.solucionador import resolver_sistema
from src.visualizacion import generar_reporte_completo

# Inicializar parámetros
params = Parametros(material='Al')

# Generar mallas
mallas = generar_todas_mallas(params)

# Ejecutar simulación
resultados, metricas = resolver_sistema(
    params=params,
    mallas=mallas,
    t_max=60.0,
    epsilon=1e-3
)

# Generar visualizaciones
generar_reporte_completo(resultados, mallas, params)
```

Para más detalles, consulta: `docs/guias/INSTRUCCIONES_USO.txt`

## 💻 Uso en Jupyter Notebook y Spyder

### 📓 Jupyter Notebook

Jupyter Notebook es ideal para exploración interactiva y visualización de resultados paso a paso.

#### 1. Instalación de Jupyter

```bash
# Instalar Jupyter Notebook
pip install jupyter notebook

# O instalar JupyterLab (versión moderna)
pip install jupyterlab
```

#### 2. Iniciar Jupyter

```bash
# Desde el directorio del proyecto
cd gpu-cooling-system

# Iniciar Jupyter Notebook
jupyter notebook

# O iniciar JupyterLab
jupyter lab
```

#### 3. Ejemplo de Uso en Notebook

Crea un nuevo notebook y ejecuta las celdas siguientes:

**Celda 1: Imports y configuración**
```python
# Configuración inicial
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Agregar el directorio src al path
sys.path.append('src')

# Imports del proyecto
from parametros import Parametros
from mallas import generar_mallas

# Configuración de matplotlib para gráficos inline
%matplotlib inline
plt.style.use('seaborn-v0_8-darkgrid')
```

**Celda 2: Inicialización de parámetros**
```python
# Crear parámetros para Aluminio
params_al = Parametros(material='aluminio')

# Mostrar propiedades del material
print(f"Material: Aluminio 6061")
print(f"Conductividad térmica: {params_al.k_placa:.2f} W/m·K")
print(f"Difusividad térmica: {params_al.alpha_placa:.2e} m²/s")
```

**Celda 3: Generar mallas**
```python
# Generar mallas para todos los dominios
mallas = generar_mallas(params_al)

# Visualizar información de las mallas
print(f"Malla fluido: {mallas['fluido']['N_x']} nodos")
print(f"Malla placa: {mallas['placa']['N_x']}x{mallas['placa']['N_y']} nodos")
print(f"Malla aletas: {mallas['aletas']['N_r']}x{mallas['aletas']['N_theta']} nodos")
```

**Celda 4: Visualización de mallas**
```python
# Graficar la geometría del sistema
from mallas import visualizar_mallas

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
visualizar_mallas(mallas, axes)
plt.tight_layout()
plt.show()
```

**Celda 5: Ejecutar simulación (en desarrollo)**
```python
# Simulación del sistema (cuando esté completo)
# from solucionador import ejecutar_simulacion
# resultados = ejecutar_simulacion(params_al, mallas, t_final=100.0)
```

#### 4. Tips para Jupyter Notebook

- **Restart & Run All**: Usa `Kernel > Restart & Run All` para verificar que todo funciona desde cero
- **Autocomplete**: Presiona `Tab` para autocompletar código y ver métodos disponibles
- **Ayuda rápida**: Usa `Shift+Tab` dentro de una función para ver su documentación
- **Guardar figuras**: 
  ```python
  fig.savefig('resultados/figuras/mi_grafico.png', dpi=300, bbox_inches='tight')
  ```
- **Progress bars**: Las barras de progreso de `tqdm` se visualizan automáticamente en notebooks

### 🔬 Spyder

Spyder es un IDE científico con editor, consola y explorador de variables integrados.

#### 1. Instalación de Spyder

```bash
# Instalar Spyder
pip install spyder

# O instalarlo con Anaconda (recomendado)
conda install spyder
```

#### 2. Configuración del Proyecto en Spyder

1. **Abrir Spyder**:
   ```bash
   spyder
   ```

2. **Configurar directorio de trabajo**:
   - Ve a `Tools > Preferences > Current Working Directory`
   - Selecciona: "The following directory"
   - Navega a la carpeta `gpu-cooling-system`

3. **Configurar Python path**:
   - Ve a `Tools > Preferences > Python Interpreter`
   - Selecciona: "Use the following Python interpreter"
   - Elige el intérprete donde instalaste las dependencias

#### 3. Estructura de Trabajo en Spyder

**Archivo: `test_simulacion.py` (crear en el directorio raíz)**

```python
"""
Script de prueba para el sistema de enfriamiento GPU
Ejecutar en Spyder para análisis interactivo
"""

import numpy as np
import matplotlib.pyplot as plt
from src.parametros import Parametros
from src.mallas import generar_mallas

# Configuración
DEBUG = True
MATERIAL = 'aluminio'  # o 'acero'

def main():
    """Función principal de prueba"""
    
    # 1. Inicializar parámetros
    print("=" * 60)
    print("SISTEMA DE ENFRIAMIENTO GPU - Test de Simulación")
    print("=" * 60)
    
    params = Parametros(material=MATERIAL)
    print(f"\n✓ Parámetros inicializados para {MATERIAL.upper()}")
    
    # 2. Generar mallas
    mallas = generar_mallas(params)
    print(f"✓ Mallas generadas exitosamente")
    
    # 3. Mostrar información
    print("\n" + "-" * 60)
    print("INFORMACIÓN DE MALLAS")
    print("-" * 60)
    print(f"Fluido:  {mallas['fluido']['N_x']} nodos en x")
    print(f"Placa:   {mallas['placa']['N_x']} × {mallas['placa']['N_y']} nodos")
    print(f"Aletas:  {mallas['aletas']['N_r']} × {mallas['aletas']['N_theta']} nodos")
    
    # 4. Visualización (opcional)
    if DEBUG:
        print("\n✓ Generando visualizaciones...")
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        # visualizar_mallas(mallas, axes)
        plt.tight_layout()
        plt.show()
    
    print("\n" + "=" * 60)
    print("✓ Test completado exitosamente")
    print("=" * 60)
    
    return params, mallas

# Ejecutar
if __name__ == "__main__":
    params, mallas = main()
```

#### 4. Uso del Explorador de Variables en Spyder

Después de ejecutar el script, puedes inspeccionar las variables en el panel "Variable Explorer":

- **`params`**: Ver todos los parámetros del sistema
- **`mallas`**: Explorar las mallas generadas (diccionarios anidados)
- **Arrays de NumPy**: Doble click para ver el contenido en formato tabla
- **Gráficos**: Se muestran automáticamente en el panel "Plots"

#### 5. Uso de la Consola IPython en Spyder

Después de ejecutar el script, la consola mantiene las variables en memoria:

```python
# En la consola IPython de Spyder:

# Inspeccionar parámetros
params.k_placa
params.alpha_placa

# Acceder a mallas
mallas['fluido']['x']
mallas['placa']['X']

# Hacer plots adicionales
import matplotlib.pyplot as plt
plt.figure()
plt.plot(mallas['fluido']['x'], label='Posiciones en x')
plt.legend()
plt.show()
```

#### 6. Tips para Spyder

- **Ejecutar líneas seleccionadas**: Selecciona código y presiona `F9`
- **Ejecutar celda**: Define celdas con `#%%` y ejecútalas con `Ctrl+Enter`
  ```python
  #%% Celda 1: Imports
  import numpy as np
  
  #%% Celda 2: Parámetros
  params = Parametros(material='aluminio')
  ```
- **Variable Explorer**: Doble click en arrays para ver valores
- **Plots interactivos**: Cambia a `Tools > Preferences > IPython Console > Graphics` y selecciona "Automatic"
- **Debugging**: Coloca breakpoints haciendo click en el margen izquierdo del editor

### 🔄 Comparación: Jupyter vs Spyder

| Característica | Jupyter Notebook | Spyder |
|----------------|------------------|--------|
| **Mejor para** | Análisis exploratorio, reportes | Desarrollo, debugging |
| **Interfaz** | Web browser | Aplicación de escritorio |
| **Ejecución** | Por celdas | Por líneas/archivo completo |
| **Variables** | Magic commands (`%whos`) | Variable Explorer gráfico |
| **Documentación** | Markdown + código mezclado | Comentarios en código |
| **Debugging** | Básico | Avanzado (breakpoints) |
| **Gráficos** | Inline automático | Panel separado |
| **Compartir** | Fácil (archivo .ipynb) | Script .py estándar |

### 📚 Recursos Adicionales

- **Documentación Jupyter**: https://jupyter-notebook.readthedocs.io/
- **Documentación Spyder**: https://docs.spyder-ide.org/
- **Atajos de teclado Jupyter**: Presiona `H` en modo comando
- **Atajos de teclado Spyder**: `Help > Shortcuts Summary`

## 📊 Resultados

Los resultados de la simulación incluyen:
- Distribución de temperatura en función del tiempo
- Tiempo de estabilización térmica
- Perfiles de temperatura en diferentes instantes
- Comparación entre materiales (Aluminio vs. Acero Inoxidable)

## 📝 Documentación

### Documentación Técnica del Problema (`contexto/`)

- `00_guia_implementacion.md` - Guía paso a paso de implementación
- `01_contexto_proyecto.md` - Descripción general y objetivos
- `02_parametros_sistema.md` - Valores numéricos y propiedades
- `03_ecuaciones_gobernantes.md` - Formulación matemática
- `04_condiciones_frontera.md` - Condiciones de frontera e interfaces
- `05_discretizacion_numerica.md` - Esquemas numéricos implementados
- `06_herramientas_desarrollo.md` - Setup y workflow de desarrollo

### Documentación de Análisis (`docs/analisis/`)

- `ANALISIS_INGENIERIL_RESULTADOS.md` - Interpretación completa de resultados (833 líneas)
- `ENTREGABLES_PRESENTACION.md` - Guía para presentación en clase
- `codigo_resumen_presentacion.py` - Código ejecutable con ecuaciones principales

### Guías de Uso (`docs/guias/`)

- `INSTRUCCIONES_USO.txt` - Manual completo (Terminal, Jupyter, Spyder)
- `README_INTERFAZ.md` - Guía de la interfaz web Streamlit
- `COMANDOS_STREAMLIT.txt` - Referencia rápida de comandos

### Notas de Desarrollo (`docs/notas/`)

- Actualizaciones de progreso, correcciones, y decisiones técnicas
- Resumen de convergencia y testing
- Instrucciones específicas para visualizaciones

### Validación de Solvers (`docs/`)

- `adr/` - Architecture Decision Records
- Validaciones exhaustivas de `placa.py` y `aletas.py`

## 🧪 Testing

```bash
# Ejecutar tests (en desarrollo)
pytest tests/
```

## 📈 Estado del Proyecto

**Estado actual**: ✅ **COMPLETO Y FUNCIONAL**

Ver `logs/worklog.md` para el registro detallado de progreso (~2,600 líneas) y decisiones técnicas.

### ✅ Componentes Completados (100%)

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| `parametros.py` | ✅ | Clase completa con validaciones, 543 líneas |
| `mallas.py` | ✅ | Generación 1D/2D cartesiano/cilíndrico, 458 líneas |
| `fluido.py` | ✅ | Solver 1D advección-difusión, 270 líneas |
| `placa.py` | ✅ | Solver 2D FTCS + Robin BCs, 373 líneas |
| `aletas.py` | ✅ | Solver 2D cilíndrico + L'Hôpital r=0, 692 líneas |
| `acoplamiento.py` | ✅ | Interpolación fluido-placa-aletas, 717 líneas |
| `solucionador.py` | ✅ | Bucle temporal + convergencia, 650+ líneas |
| `visualizacion.py` | ✅ | 9 funciones de graficación, 1,050+ líneas |
| `main.py` | ✅ | CLI + menú interactivo, 850+ líneas |
| `interfaz_web.py` | ✅ | Interfaz Streamlit, 450+ líneas |

### 📊 Métricas del Proyecto

- **Líneas de código fuente**: ~5,000 líneas
- **Líneas de documentación**: ~3,500 líneas
- **Total de archivos**: 50+ archivos
- **Tiempo de desarrollo**: ~15 horas (registradas)
- **Commits**: 10+ commits principales
- **Tests ejecutados**: 100+ validaciones exitosas
- **Simulaciones completadas**: Al (60s) + SS (60s)
- **Figuras generadas**: 18 (9 Al + 9 SS)

### 🎓 Entregables Académicos

- ✅ Análisis ingenieril completo (833 líneas)
- ✅ Código resumido para presentación (485 líneas)
- ✅ Guía de entregables (282 líneas)
- ✅ 18 figuras de alta calidad (DPI 300)
- ✅ Manual de uso exhaustivo (500+ líneas)

## 👤 Autor

**Adrián Vargas Tijerino** (C18332)  
Curso: IQ-0331 Fenómenos de Transferencia

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la Universidad de Costa Rica.

## 🤝 Contribuciones

Este es un proyecto académico. Para consultas o sugerencias, por favor contactar al autor.

---

**Nota**: Este proyecto utiliza métodos numéricos avanzados para resolver ecuaciones diferenciales parciales acopladas. Se recomienda familiaridad con transferencia de calor y métodos numéricos para su comprensión completa.

