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
├── src/                      # Código fuente principal
│   ├── parametros.py         # Parámetros físicos y numéricos del sistema
│   ├── mallas.py             # Generación de mallas para cada dominio
│   ├── fluido.py             # Solver 1D para el flujo de agua
│   ├── placa.py              # Solver 2D para la placa base
│   ├── aletas.py             # Solver 2D cilíndrico para aletas
│   └── acoplamiento.py       # Acoplamiento entre dominios
├── contexto/                 # Documentación técnica del proyecto
│   ├── 01_contexto_proyecto.md
│   ├── 02_parametros_sistema.md
│   ├── 03_ecuaciones_gobernantes.md
│   ├── 04_condiciones_frontera.md
│   ├── 05_discretizacion_numerica.md
│   └── 06_herramientas_desarrollo.md
├── docs/                     # Documentación de validación
│   ├── validacion_solver_placa.md
│   └── validacion_solver_aletas.md
├── tests/                    # Tests unitarios y de integración
├── resultados/               # Resultados de simulaciones
│   ├── datos/                # Archivos de datos generados
│   └── figuras/              # Gráficos y visualizaciones
├── requirements.txt          # Dependencias del proyecto
└── worklog.md                # Registro detallado de desarrollo
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone https://github.com/[tu-usuario]/gpu-cooling-system.git
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

```python
# Ejemplo básico de uso (en desarrollo)
from src.parametros import Parametros
from src.mallas import generar_mallas
from src.solucionador import ejecutar_simulacion

# Inicializar parámetros
params = Parametros(material='aluminio')

# Generar mallas
mallas = generar_mallas(params)

# Ejecutar simulación
resultados = ejecutar_simulacion(params, mallas)
```

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

La documentación técnica detallada se encuentra en la carpeta `/contexto/`:

- **Contexto del proyecto**: Descripción general y objetivos
- **Parámetros del sistema**: Valores numéricos y propiedades
- **Ecuaciones gobernantes**: Formulación matemática
- **Condiciones de frontera**: BCs e interfaces
- **Discretización numérica**: Esquemas implementados
- **Herramientas de desarrollo**: Setup y workflow

## 🧪 Testing

```bash
# Ejecutar tests (en desarrollo)
pytest tests/
```

## 📈 Estado del Proyecto

**Estado actual**: En desarrollo activo

Ver `worklog.md` para el registro detallado de progreso y decisiones técnicas.

### Componentes Completados
- ✅ Clase de parámetros
- ✅ Generación de mallas
- ✅ Solver del fluido (1D)
- ✅ Solver de la placa (2D)
- ✅ Solver de aletas (2D cilíndrico)
- ✅ Sistema de acoplamiento térmico

### Pendientes
- 🔄 Bucle temporal completo
- 🔄 Criterio de convergencia a estado estacionario
- 🔄 Validación completa
- 🔄 Optimización de rendimiento

## 👤 Autor

**Adrián Vargas Tijerino** (C18332)  
Curso: IQ-0331 Fenómenos de Transferencia

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la Universidad de Costa Rica.

## 🤝 Contribuciones

Este es un proyecto académico. Para consultas o sugerencias, por favor contactar al autor.

---

**Nota**: Este proyecto utiliza métodos numéricos avanzados para resolver ecuaciones diferenciales parciales acopladas. Se recomienda familiaridad con transferencia de calor y métodos numéricos para su comprensión completa.

