# 🌡️ Gráfico de Distribución Espacial de Temperatura

## 📋 Descripción

Nueva función de visualización que muestra la **distribución espacial completa** del sistema de enfriamiento GPU, incluyendo:

- ✅ Placa base con perfil de temperatura
- ✅ 3 aletas cilíndricas en sus posiciones reales
- ✅ Zona de agua fluyendo entre las aletas
- ✅ Perfiles de temperatura en cortes verticales

---

## 🎨 Composición del Gráfico

### Panel Superior: Vista Frontal (x-y)

```
         🌊 Agua (zona semitransparente cyan)
    ╔═══════════════════════════════════════╗
    ║     🔴         🔴         🔴         ║  <- 3 Aletas semicirculares
    ║   (5mm)     (15mm)     (25mm)       ║     con temperatura
    ║                                      ║
    ╠══════════════════════════════════════╣  <- Interfaz placa-agua
    ║                                      ║
    ║         🔥 PLACA BASE 🔥             ║  <- Contorno de temperatura
    ║      (contourf con colormap)        ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    0mm                                 30mm
```

**Elementos visuales:**
- **Placa**: Contorno relleno (`contourf`) con colormap 'hot'
- **Aletas**: Semicírculos rellenos con color según T promedio
- **Agua**: Rectángulo semitransparente (alpha=0.15, cyan)
- **Etiquetas**: Temperatura de cada aleta sobre semicírculo
- **Líneas**: Interfaz placa-agua (línea negra punteada)

### Panel Inferior: Perfiles Verticales

Muestra **3 perfiles de temperatura** en cortes verticales:
- Perfil 1: x = 5 mm (debajo de Aleta 1)
- Perfil 2: x = 15 mm (debajo de Aleta 2)
- Perfil 3: x = 25 mm (debajo de Aleta 3)

Cada perfil muestra:
- 📈 Línea continua: Temperatura en la placa (y = 0 → 10 mm)
- 🔺 Punto triangular: Temperatura promedio de la aleta correspondiente

---

## 🚀 Uso Rápido

### Opción 1: Script Standalone

```bash
cd /Users/randallbonilla/Desktop/python-adrian
python3 ejemplo_distribucion_espacial.py
```

**Salida:**
```
✅ GRÁFICO GENERADO EXITOSAMENTE
📊 Figura guardada en:
   resultados/figuras/distribucion_espacial_Al_t5.00s.png
```

### Opción 2: Importar en Python

```python
from src.visualizacion import graficar_distribucion_espacial_completa, cargar_resultados
from src.parametros import Parametros
from src.mallas import generar_todas_mallas

# Cargar datos
resultados = cargar_resultados("resultados_Aluminio.npz")
params = Parametros(material='Al')
mallas = generar_todas_mallas(params)

# Generar gráfico
fig = graficar_distribucion_espacial_completa(
    resultados=resultados,
    mallas=mallas,
    params=params,
    tiempo_idx=-1,      # Último instante temporal
    guardar=True,        # Guardar en resultados/figuras/
    mostrar=False        # No mostrar interactivamente
)
```

### Opción 3: Incluido en Reporte Completo

```python
from src.visualizacion import generar_reporte_completo

# Genera TODAS las figuras, incluyendo distribución espacial
rutas = generar_reporte_completo(resultados, mallas, params)

# La distribución espacial está en:
print(rutas['distribucion'])
```

---

## 📐 Geometría del Sistema

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `L_x` | 30 mm | Longitud total de la placa |
| `e_base` | 10 mm | Espesor de la placa |
| `r` | 4 mm | Radio de las aletas (semicilindros) |
| `x_aleta_1` | 5 mm | Posición centro Aleta 1 |
| `x_aleta_2` | 15 mm | Posición centro Aleta 2 |
| `x_aleta_3` | 25 mm | Posición centro Aleta 3 |
| Altura aletas | 4 mm | Desde y=10mm hasta y=14mm |

**Espaciamiento entre aletas:**
- Aleta 1 ↔ Aleta 2: 10 mm
- Aleta 2 ↔ Aleta 3: 10 mm
- Separación uniforme: 10 mm

---

## 🎨 Escala de Temperatura

- **Colormap**: 'hot' (rojo caliente → amarillo → blanco)
- **Rango**: Escala unificada para placa y aletas
  - `T_min`: Temperatura mínima del sistema
  - `T_max`: Temperatura máxima del sistema
- **Colorbar**: En el lado derecho del panel superior

**Interpretación de colores:**
- 🔴 **Rojo oscuro**: Temperaturas bajas (~23°C)
- 🟠 **Naranja**: Temperaturas intermedias (~40-60°C)
- 🟡 **Amarillo**: Temperaturas altas (~70-80°C)
- ⚪ **Blanco**: Temperaturas muy altas (>85°C)

---

## 📊 Información Mostrada

### Vista Frontal:
1. **Contorno de temperatura** de la placa completa
2. **Posición y forma** de las 3 aletas
3. **Temperatura promedio** de cada aleta (etiqueta sobre semicírculo)
4. **Zona de agua** (región cyan entre placa y aletas)
5. **Interfaz placa-agua** (línea punteada negra)

### Perfiles Verticales:
1. **Gradiente térmico** en dirección vertical (y)
2. **Comparación** entre las 3 posiciones de aletas
3. **Discontinuidad térmica** en interfaz placa-agua
4. **Líneas de referencia**:
   - Interfaz placa-agua (y = 10 mm)
   - Centro de aletas (y = 14 mm)

---

## 🔍 Ejemplo de Resultados

### Para Aluminio a t=5.00s:

```
🌡️ Temperaturas finales:
   - Fluido:  79.7 °C
   - Placa:   29.3 °C
   - Aletas:  29.0 °C

📊 Observaciones:
   - Aletas ligeramente más frías que placa (buena transferencia)
   - Gradiente térmico visible en dirección vertical
   - Agua a ~80°C mantiene flujo constante
   - Sistema lejos de estado estacionario (t=5s)
```

---

## 📁 Archivos Generados

```
resultados/figuras/
└── distribucion_espacial_{material}_t{tiempo}s.png

Ejemplo:
- distribucion_espacial_Al_t5.00s.png (541 KB)
- distribucion_espacial_SS_t30.00s.png
```

**Características del archivo:**
- Formato: PNG
- Resolución: 300 DPI (alta calidad para publicación)
- Tamaño típico: 400-600 KB
- Dimensiones: 1600 × 1000 px

---

## 🛠️ Parámetros de la Función

```python
def graficar_distribucion_espacial_completa(
    resultados: Dict,      # Resultados de la simulación (.npz)
    mallas: Dict,          # Mallas del sistema
    params: Parametros,    # Parámetros del sistema
    tiempo_idx: int = -1,  # Índice temporal (-1 = último)
    guardar: bool = True,  # Si guardar en archivo
    nombre_archivo: Optional[str] = None,  # Nombre custom
    mostrar: bool = False  # Si mostrar interactivamente
) -> plt.Figure
```

**Argumentos opcionales:**
- `tiempo_idx`: Índice del instante a graficar
  - `-1`: Último instante (default)
  - `0`: Instante inicial
  - `n`: Cualquier índice válido
- `guardar`: Si False, no guarda archivo
- `nombre_archivo`: Nombre personalizado (default: auto-generado)
- `mostrar`: Si True, muestra gráfico interactivo con `plt.show()`

---

## 💡 Casos de Uso

### 1. Análisis de Distribución Térmica
Ver cómo se distribuye el calor en todo el sistema de manera integrada.

### 2. Presentaciones y Reportes
Gráfico ideal para mostrar la geometría real del sistema con temperaturas.

### 3. Validación de Diseño
Verificar que las aletas están posicionadas correctamente.

### 4. Comparación de Materiales
Generar para Al y SS para comparar eficiencia de enfriamiento.

### 5. Evolución Temporal
Generar múltiples gráficos en diferentes instantes:
```python
for idx in [0, len(tiempo)//4, len(tiempo)//2, -1]:
    fig = graficar_distribucion_espacial_completa(
        resultados, mallas, params,
        tiempo_idx=idx,
        guardar=True
    )
```

---

## 🎯 Ventajas de Esta Visualización

| Aspecto | Beneficio |
|---------|-----------|
| **Integrador** | Muestra placa + aletas + agua en un solo gráfico |
| **Geometría real** | Posiciones exactas de aletas (5, 15, 25 mm) |
| **Escala unificada** | Colores comparables entre placa y aletas |
| **Vista completa** | Panel frontal + perfiles verticales |
| **Profesional** | Alta calidad (DPI 300) para publicación |
| **Informativo** | Etiquetas con temperaturas de cada aleta |
| **Intuitivo** | Agua visible, interfaz clara |

---

## 📚 Referencias

- **Código fuente**: `src/visualizacion.py` (líneas 680-862)
- **Script ejemplo**: `ejemplo_distribucion_espacial.py`
- **Función relacionada**: `generar_reporte_completo()` (incluye automáticamente)

---

## 🐛 Troubleshooting

### Problema: "No se encontró resultados_Aluminio.npz"
**Solución**: Ejecuta primero una simulación:
```bash
python3 src/solucionador.py
```

### Problema: "IndexError" en mallas
**Solución**: La función maneja automáticamente mallas 1D y 2D. Si persiste, verifica que `mallas` se generó correctamente:
```python
from src.mallas import generar_todas_mallas
mallas = generar_todas_mallas(params)
```

### Problema: Figura muy grande/pequeña
**Solución**: Modifica el tamaño en el código:
```python
# En línea 736 de visualizacion.py
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))  # Ajustar (width, height)
```

---

## ✅ Checklist de Validación

Antes de usar en producción, verifica:

- [ ] Resultados de simulación disponibles
- [ ] Aletas en posiciones correctas (5, 15, 25 mm)
- [ ] Escala de temperatura lógica (20-85 °C típico)
- [ ] Zona de agua visible
- [ ] Colorbar presente
- [ ] Figura guardada en `resultados/figuras/`
- [ ] Archivo PNG de ~500 KB

---

**Última actualización**: 6 de Octubre, 2025  
**Versión**: 1.0  
**Autor**: Sistema de Simulación

---

🎉 **¡Disfruta visualizando la distribución espacial de temperatura!**
