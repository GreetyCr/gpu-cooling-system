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

