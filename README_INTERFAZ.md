# 🌡️ Simulador de Enfriamiento GPU - Guía Rápida

Sistema de Transferencia de Calor Multi-dominio con Aletas Cilíndricas

---

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
cd /Users/randallbonilla/Desktop/python-adrian
pip install -r requirements.txt
```

### 2. Ejecutar Simulación

**Opción A: Terminal (modo texto)**
```bash
python3 -c "
from src.parametros import Parametros
from src.mallas import generar_todas_mallas
from src.solucionador import resolver_sistema

params = Parametros(material='Al')
mallas = generar_todas_mallas(params)
resultados = resolver_sistema(params, mallas, t_max=10.0, verbose=True)
"
```

**Opción B: Interfaz Web (RECOMENDADO) 🎨**
```bash
streamlit run interfaz_web.py
```

Abre automáticamente en: http://localhost:8501

---

## 📱 Interfaz Web - Vista Previa

### Panel de Control
```
⚙️ Configuración
┌──────────────────────────────┐
│ Material: Aluminio 6061      │
│ Tiempo: [5s ----●---- 60s]   │
│ Convergencia: 1e-3 K/s       │
│ Guardar cada: 200 pasos      │
│ ☑ Balance Energético         │
└──────────────────────────────┘

     [🚀 INICIAR SIMULACIÓN]
```

### Resultados Interactivos

#### Tab 1: 📈 Evolución Temporal
- Gráfico de T vs tiempo para fluido, placa y aletas
- Temperaturas finales detalladas
- Tasas de cambio (dT/dt)

#### Tab 2: 🗺️ Campos de Temperatura
- Mapa de calor 2D de la placa (selector temporal)
- Perfil longitudinal en centro de placa
- Escala de colores "hot" (azul → rojo)

#### Tab 3: ⚡ Balance Energético
- Q_in (entrada), Q_out (salida), dE/dt (acumulación)
- Error relativo (%) vs tiempo
- Validación de conservación de energía

#### Tab 4: 💾 Datos
- Descarga de resultados .npz
- Código de ejemplo para cargar datos
- Información del archivo guardado

---

## 📊 Resultados Típicos

### Material: Aluminio 6061 | t_max = 30s

| Tiempo | T_fluido | T_placa | T_aletas | max\|dT/dt\| |
|--------|----------|---------|----------|--------------|
| 0.0 s  | 24.0°C   | 23.0°C  | 23.0°C   | 12,400 K/s   |
| 0.5 s  | 79.6°C   | 23.5°C  | 23.2°C   | 1.94 K/s     |
| 10.0 s | 79.7°C   | 35.1°C  | 34.8°C   | 1.09 K/s     |
| 30.0 s | 79.8°C   | ~45°C   | ~44°C    | ~0.5 K/s     |

**Convergencia**: Típicamente alcanzada en 40-60 segundos (simulación física)

**Balance Energético**:
- Q_in inicial: ~7,800 W (calentamiento masivo)
- Q_in final: ~60 W (casi en equilibrio)
- Error: <40% (aceptable en transitorios)

---

## 🎯 Modos de Uso Disponibles

### 1. 💻 Terminal
- **Ventajas**: Control total, scriptable, automatizable
- **Ideal para**: Análisis batch, HPC, debugging
- **Ver**: `INSTRUCCIONES_USO.txt` sección 2

### 2. 📓 Jupyter Notebook
- **Ventajas**: Exploración interactiva, documentación viva
- **Ideal para**: Análisis exploratorio, reportes
- **Ver**: `INSTRUCCIONES_USO.txt` sección 3

### 3. 🐍 Spyder IDE
- **Ventajas**: Debugging visual, Variable Explorer
- **Ideal para**: Desarrollo, depuración detallada
- **Ver**: `INSTRUCCIONES_USO.txt` sección 4

### 4. 🌐 Interfaz Web (Streamlit)
- **Ventajas**: No requiere programación, visualización rica
- **Ideal para**: Presentaciones, usuarios no técnicos
- **Ver**: `INSTRUCCIONES_USO.txt` sección 5

---

## 📁 Estructura del Proyecto

```
python-adrian/
├── src/
│   ├── parametros.py      # Parámetros del sistema (✅)
│   ├── mallas.py          # Generación de mallas (✅)
│   ├── fluido.py          # Solver 1D fluido (✅)
│   ├── placa.py           # Solver 2D placa (✅)
│   ├── aletas.py          # Solver 2D cilíndrico aletas (✅)
│   ├── acoplamiento.py    # Interfaces térmicas (✅)
│   ├── solucionador.py    # Bucle temporal maestro (✅)
│   └── visualizacion.py   # Gráficos avanzados (⏳)
│
├── interfaz_web.py        # Interfaz Streamlit (✅)
├── main.py                # Script principal (⏳)
│
├── contexto/              # Documentación técnica
│   ├── 01_contexto_proyecto.md
│   ├── 02_parametros_sistema.md
│   ├── 03_ecuaciones_gobernantes.md
│   ├── 04_condiciones_frontera.md
│   ├── 05_discretizacion_numerica.md
│   └── 06_herramientas_desarrollo.md
│
├── docs/                  # Validaciones de solvers
│   ├── validacion_solver_placa.md
│   └── validacion_solver_aletas.md
│
├── resultados/            # Salidas de simulaciones
│   ├── datos/             # Archivos .npz
│   └── figuras/           # Gráficos generados
│
├── INSTRUCCIONES_USO.txt  # Guía completa de uso (✅)
├── README_INTERFAZ.md     # Este archivo
├── worklog.md             # Historial de desarrollo
└── requirements.txt       # Dependencias Python
```

**Progreso**: 9/11 módulos completados (82%)

---

## 🔧 Configuración Avanzada

### Cambiar Material

```python
# Aluminio 6061 (por defecto)
params = Parametros(material="Al")

# Acero Inoxidable 304
params = Parametros(material="SS")
```

### Ajustar Tiempo de Simulación

```python
# Simulación rápida (10 segundos)
resultados = resolver_sistema(..., t_max=10.0)

# Simulación completa (60 segundos)
resultados = resolver_sistema(..., t_max=60.0)
```

### Criterio de Convergencia

```python
# Más estricto (converge más lento)
resultados = resolver_sistema(..., epsilon=1e-4)

# Menos estricto (converge más rápido)
resultados = resolver_sistema(..., epsilon=1e-2)
```

---

## 💾 Cargar Resultados Guardados

```python
import numpy as np

# Cargar simulación previa
data = np.load('resultados/datos/resultados_Aluminio.npz', allow_pickle=True)

# Extraer datos
tiempo = data['tiempo']
T_fluido = data['T_fluido']
T_placa = data['T_placa']
T_aletas = data['T_aletas']
convergencia = data['convergencia'].item()
metricas = data['metricas'].item()

# Temperatura promedio final de la placa
T_p_final = T_placa[-1].mean() - 273.15  # En °C
print(f"Temperatura final: {T_p_final:.1f} °C")
```

---

## 🆘 Solución de Problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: src` | Ejecutar desde directorio raíz del proyecto |
| Simulación muy lenta | Reducir `t_max` o aumentar `guardar_cada` |
| Error de memoria | Reducir `t_max` o aumentar `guardar_cada` |
| Streamlit no abre | Abrir manualmente: http://localhost:8501 |
| Temperaturas NaN/Inf | Reinstalar dependencias, verificar Python ≥3.8 |

**Ver más**: `INSTRUCCIONES_USO.txt` sección 7 (Solución de Problemas)

---

## ⏱️ Tiempos de Ejecución

| t_max | Pasos | Tiempo Real |
|-------|-------|-------------|
| 10 s  | 20,000 | ~2-3 min |
| 30 s  | 60,000 | ~5-7 min |
| 60 s  | 120,000 | ~10-15 min |

*En MacBook Pro M1/M2 o equivalente*

**Factores que afectan el tiempo**:
- Material (Al más rápido que SS)
- `guardar_cada` (mayor = más rápido)
- Balance energético (+20% tiempo)

---

## 🎓 Recursos Adicionales

- **Documentación Técnica**: Ver carpeta `contexto/`
- **Validaciones**: Ver carpeta `docs/`
- **Ecuaciones**: `contexto/03_ecuaciones_gobernantes.md`
- **Parámetros**: `contexto/02_parametros_sistema.md`
- **Historial**: `worklog.md`

---

## 📞 Contacto

**Proyecto**: Sistema de Enfriamiento GPU con Aletas Cilíndricas  
**Estudiante**: Adrián Vargas Tijerino (C18332)  
**Curso**: IQ-0331 Fenómenos de Transferencia  
**Versión**: 1.0  
**Fecha**: Octubre 2025

---

## 📄 Licencia

Proyecto académico - Universidad de Costa Rica  
Escuela de Ingeniería Química

---

**¿Listo para empezar?**

```bash
streamlit run interfaz_web.py
```

🌡️ **¡Feliz simulación!** 🚀
