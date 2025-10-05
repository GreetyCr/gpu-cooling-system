# Herramientas y Configuración para Desarrollo

## 1. Python - Versión y Entorno

### Versión Requerida
- **Python 3.10** o superior (recomendado: Python 3.11)

### Gestión de Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

---

## 2. Librerías Python Esenciales

### Instalación Completa
```bash
pip install numpy scipy matplotlib pandas
```

### Librerías Núcleo

#### NumPy (versión >= 1.24.0)
**Propósito:** Operaciones numéricas y manejo de arrays
```python
import numpy as np
```
**Uso específico:**
- Creación y manipulación de mallas 2D
- Operaciones vectorizadas para eficiencia
- Cálculo de derivadas numéricas
- Almacenamiento de campos de temperatura

#### SciPy (versión >= 1.10.0)
**Propósito:** Algoritmos científicos avanzados
```python
from scipy import interpolate
from scipy.integrate import solve_ivp, odeint
from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import spsolve
```
**Uso específico:**
- `interpolate.RectBivariateSpline`: Interpolación bilineal para interfaz placa-aleta
- `interpolate.interp1d`: Interpolación 1D para fluido-placa
- Solvers implícitos (opcional para estabilidad)
- Verificación de convergencia

#### Matplotlib (versión >= 3.7.0)
**Propósito:** Visualización de resultados
```python
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
```
**Uso específico:**
- Gráficos de contornos de temperatura 2D
- Perfiles de temperatura 1D vs tiempo
- Animaciones del proceso transitorio
- Gráficos de superficie 3D (opcional)

#### Pandas (versión >= 2.0.0)
**Propósito:** Manejo de datos tabulares y análisis
```python
import pandas as pd
```
**Uso específico:**
- Almacenamiento de resultados (temperatura vs tiempo)
- Exportación a CSV para análisis posterior
- Construcción de tablas de convergencia
- Comparación entre materiales (Al vs SS)

---

## 3. Librerías Adicionales Recomendadas

### Numba (versión >= 0.57.0)
**Propósito:** Aceleración JIT de bucles
```bash
pip install numba
```
```python
from numba import jit, prange
```
**Uso específico:**
- Decorar funciones de actualización con `@jit(nopython=True)`
- Acelerar bucles de tiempo
- Reducir tiempo de cómputo para mallas finas

**Ejemplo:**
```python
@jit(nopython=True)
def actualizar_placa(T, Fo_x, Fo_y, Nx, Ny):
    T_new = T.copy()
    for i in range(1, Nx-1):
        for j in range(1, Ny-1):
            T_new[i,j] = T[i,j] + Fo_x*(T[i+1,j] - 2*T[i,j] + T[i-1,j]) + \
                                   Fo_y*(T[i,j+1] - 2*T[i,j] + T[i,j-1])
    return T_new
```

### Seaborn (versión >= 0.12.0)
**Propósito:** Visualizaciones estadísticas mejoradas
```bash
pip install seaborn
```
```python
import seaborn as sns
```
**Uso específico:**
- Mapas de calor de distribución de temperatura
- Gráficos comparativos entre materiales
- Estilos visuales profesionales

### tqdm (versión >= 4.65.0)
**Propósito:** Barras de progreso
```bash
pip install tqdm
```
```python
from tqdm import tqdm
```
**Uso específico:**
- Monitorear progreso de simulación temporal
- Estimar tiempo restante de cómputo

**Ejemplo:**
```python
for n in tqdm(range(n_steps), desc="Simulando"):
    # Código de actualización
    pass
```

---

## 4. Herramientas de Desarrollo en VSCode/Cursor

### Extensiones Esenciales de VSCode

1. **Python (Microsoft)** - ID: ms-python.python
   - IntelliSense, debugging, linting

2. **Pylance** - ID: ms-python.vscode-pylance
   - Type checking mejorado

3. **Jupyter** - ID: ms-toolsai.jupyter
   - Ejecutar notebooks interactivos

4. **autoDocstring** - ID: njpwerner.autodocstring
   - Generación automática de docstrings

5. **Error Lens** - ID: usernamehw.errorlens
   - Visualización inline de errores

### Configuración Recomendada (settings.json)
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.typeCheckingMode": "basic",
    "editor.formatOnSave": true,
    "files.autoSave": "afterDelay",
    "python.terminal.activateEnvironment": true
}
```

---

## 5. Estructura de Proyecto Recomendada

```
proyecto_enfriamiento_gpu/
│
├── venv/                      # Entorno virtual
│
├── contexto/                  # Documentos .md de contexto
│   ├── 01_contexto_proyecto.md
│   ├── 02_parametros_sistema.md
│   ├── 03_ecuaciones_gobernantes.md
│   ├── 04_condiciones_frontera.md
│   ├── 05_discretizacion_numerica.md
│   └── 06_herramientas_desarrollo.md
│
├── src/                       # Código fuente
│   ├── __init__.py
│   ├── parametros.py         # Parámetros del sistema
│   ├── mallas.py             # Generación de mallas
│   ├── fluido.py             # Solver del fluido
│   ├── placa.py              # Solver de la placa
│   ├── aletas.py             # Solver de aletas
│   ├── acoplamiento.py       # Interfaz placa-aleta
│   ├── solucionador.py       # Integración temporal
│   └── visualizacion.py      # Funciones de graficación
│
├── tests/                     # Tests unitarios
│   ├── test_mallas.py
│   ├── test_fluido.py
│   └── test_placa.py
│
├── resultados/                # Carpeta de salida
│   ├── figuras/
│   ├── datos/
│   └── animaciones/
│
├── notebooks/                 # Jupyter notebooks
│   ├── analisis_exploratorio.ipynb
│   └── comparacion_materiales.ipynb
│
├── main.py                    # Script principal
├── requirements.txt           # Dependencias
├── README.md                  # Documentación
└── .gitignore
```

---

## 6. Archivo requirements.txt

```txt
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
pandas>=2.0.0
numba>=0.57.0
seaborn>=0.12.0
tqdm>=4.65.0
jupyter>=1.0.0
black>=23.0.0
pylint>=2.17.0
pytest>=7.3.0
```

**Instalación:**
```bash
pip install -r requirements.txt
```

---

## 7. Herramientas de Debugging y Profiling

### IPython
```bash
pip install ipython
```
**Uso:** REPL mejorado para desarrollo interactivo

### Memory Profiler
```bash
pip install memory_profiler
```
**Uso:** Análisis de uso de memoria
```python
from memory_profiler import profile

@profile
def mi_funcion():
    # código
    pass
```

### Line Profiler
```bash
pip install line_profiler
```
**Uso:** Identificar líneas lentas
```python
from line_profiler import LineProfiler

lp = LineProfiler()
lp.add_function(mi_funcion)
lp.run('mi_funcion()')
lp.print_stats()
```

---

## 8. Control de Versiones

### Git
Inicializar repositorio:
```bash
git init
git add .
git commit -m "Initial commit"
```

### .gitignore Recomendado
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Jupyter
.ipynb_checkpoints/

# Resultados (opcional)
resultados/datos/*.csv
resultados/figuras/*.png
resultados/animaciones/*.mp4

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 9. Documentación y Comentarios

### Docstrings - Formato NumPy/Google
```python
def calcular_temperatura(T, alpha, dt, dx):
    """
    Calcula la evolución de temperatura usando FTCS.
    
    Parameters
    ----------
    T : np.ndarray
        Campo de temperatura actual (2D)
    alpha : float
        Difusividad térmica [m²/s]
    dt : float
        Paso de tiempo [s]
    dx : float
        Espaciamiento de malla [m]
        
    Returns
    -------
    T_new : np.ndarray
        Campo de temperatura actualizado (2D)
        
    Notes
    -----
    Esquema explícito, requiere dt < dx²/(4*alpha)
    """
    # implementación
    pass
```

---

## 10. Checklist de Configuración Inicial

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Todas las librerías instaladas (`pip install -r requirements.txt`)
- [ ] Extensiones de VSCode/Cursor instaladas
- [ ] Estructura de carpetas creada
- [ ] Git inicializado
- [ ] Documentos .md de contexto leídos
- [ ] Primer test ejecutado exitosamente

---

## 11. Comandos Útiles de Desarrollo

### Ejecutar Script Principal
```bash
python main.py
```

### Ejecutar Tests
```bash
pytest tests/
```

### Formatear Código
```bash
black src/
```

### Linting
```bash
pylint src/
```

### Generar Documentación
```bash
pip install sphinx
sphinx-quickstart docs/
sphinx-build -b html docs/ docs/_build
```

---

## 12. Consideraciones de Performance

### Para Mallas Grandes
- Usar `numba` para acelerar bucles
- Considerar solvers implícitos (más estables, pasos de tiempo mayores)
- Paralelizar actualización de aletas con `multiprocessing`

### Gestión de Memoria
- No almacenar todos los pasos de tiempo, solo cada N
- Usar `np.float32` si la precisión de `float64` no es crítica
- Limpiar variables intermedias con `del`

### Optimización
- Vectorizar operaciones en lugar de bucles cuando sea posible
- Pre-calcular constantes (Fo_x, Fo_y, etc.)
- Usar `scipy.sparse` para sistemas implícitos grandes

---

## 13. Recursos Adicionales

### Documentación Oficial
- NumPy: https://numpy.org/doc/
- SciPy: https://docs.scipy.org/doc/scipy/
- Matplotlib: https://matplotlib.org/stable/contents.html

### Tutoriales Relevantes
- CFD Python: https://github.com/barbagroup/CFDPython
- NumPy para MATLAB users: https://numpy.org/doc/stable/user/numpy-for-matlab-users.html

### Papers de Referencia
- Hensen & Nakhi (1994): Fourier and Biot numbers
- Shu & LeVeque (1991): Métodos numéricos para leyes de conservación
