# 📊 Resumen: Gráfico de Distribución Espacial en Convergencia

## 🎯 Objetivo

Generar el gráfico de distribución espacial de temperatura en el **instante donde se alcanza el estado estacionario** (convergencia).

---

## ⏱️ Estado Actual

### ✅ Gráfico Rápido Generado

**Archivo**: `resultados/figuras/distribucion_espacial_rapido_Al_t5.00s.png`

- **Tiempo**: 5.00 s
- **Estado**: Transitorio (NO es estado estacionario)
- **Temperaturas**:
  - Fluido: 79.7 °C
  - Placa: 29.3 °C
  - Aletas: 29.0 °C

### 🔄 Simulación Hasta Convergencia EN EJECUCIÓN

**Estado**: Corriendo en segundo plano
**Archivo de salida**: `convergencia_output.log`
**Tiempo estimado**: 5-10 minutos

**Progreso actual** (última actualización):
- Tiempo simulado: ~0.70 s
- max|dT/dt|: 1.54 K/s
- **Objetivo**: max|dT/dt| < 1e-3 K/s (0.001 K/s)

---

## 📂 Archivos Generados

### Disponible Ahora:

```
resultados/figuras/
└── distribucion_espacial_rapido_Al_t5.00s.png ✅
    (Gráfico al tiempo final disponible, NO convergencia)
```

### Se Generarán Al Completar:

```
resultados/figuras/
├── distribucion_espacial_convergencia_Al_tXX.XXs.png ⏳
│   (Gráfico EN el instante de convergencia)
└── distribucion_espacial_final_Al_tYY.YYs.png ⏳
    (Gráfico al tiempo final de simulación larga)
```

---

## 🔍 Monitorear Progreso

### Opción 1: Script de Monitoreo
```bash
./monitorear_convergencia.sh
```

### Opción 2: Ver Log en Tiempo Real
```bash
tail -f convergencia_output.log
```

### Opción 3: Ver Últimas Líneas
```bash
tail -n 50 convergencia_output.log
```

---

## 📊 Qué Esperar

### Estado Transitorio (t=5s, actual)
```
Fluido: 79.7 °C ━━━━━━━━━━━━━━━━━━━╸ Calentándose
Placa:  29.3 °C ━━╸░░░░░░░░░░░░░░░░ Calentándose lentamente
Aletas: 29.0 °C ━━╸░░░░░░░░░░░░░░░░ Calentándose lentamente

max|dT/dt| = 1.3 K/s  (sistema cambiando rápidamente)
```

### Estado Estacionario (t=XX.XXs, objetivo)
```
Fluido: ~79.X °C ━━━━━━━━━━━━━━━━━━━ Estable
Placa:  ~YY.Y °C ━━━━━━━━━━━━━━━━━━━ Estable
Aletas: ~ZZ.Z °C ━━━━━━━━━━━━━━━━━━━ Estable

max|dT/dt| < 0.001 K/s  (sistema prácticamente estático)
```

**Cambios esperados**:
- Placa: 29.3°C → ~40-50°C (estimado)
- Aletas: 29.0°C → ~38-48°C (estimado)
- Tiempo: ~30-60 segundos de simulación

---

## 🛠️ Scripts Disponibles

### 1. **`generar_grafico_convergencia.py`** (⏳ Ejecutándose)

**Propósito**: Ejecutar simulación completa hasta convergencia

```bash
python3 generar_grafico_convergencia.py
```

- ⏱️ Tiempo: 5-10 minutos
- 🎯 Genera gráfico en convergencia
- 💾 Guarda resultados completos
- ✅ ES LO QUE QUIERES

### 2. **`generar_grafico_rapido.py`** (✅ Completado)

**Propósito**: Gráfico con datos existentes (rápido)

```bash
python3 generar_grafico_rapido.py
```

- ⏱️ Tiempo: < 10 segundos
- 📊 Usa datos existentes (t=5s)
- ⚠️ NO es estado estacionario
- 💡 Para visualización inmediata

### 3. **`monitorear_convergencia.sh`** (🔍 Monitor)

**Propósito**: Ver progreso de la simulación

```bash
./monitorear_convergencia.sh
```

- 📊 Muestra últimas 20 líneas
- ⏱️ Estado actual de la simulación
- 🔍 Verifica si completó

---

## 📈 Interpretación de max|dT/dt|

| Rango | Significado | Estado |
|-------|-------------|--------|
| > 100 K/s | Transitorio rápido | Inicial |
| 10-100 K/s | Transitorio moderado | Calentamiento |
| 1-10 K/s | Transitorio lento | Acercándose |
| 0.1-1 K/s | Casi estacionario | Cercano |
| < 0.001 K/s | **Estado estacionario** | ✅ **OBJETIVO** |

**Actual**: ~1.3 K/s → Todavía en transitorio lento

---

## 🎯 Criterios de Convergencia

```python
epsilon = 1e-3  # 0.001 K/s

Condición: max|dT/dt| < epsilon para TODOS los dominios:
  - Fluido (60 nodos)
  - Placa (1,200 nodos)
  - Aletas (600 nodos)
```

Cuando **TODOS** los nodos tengan cambio de temperatura < 0.001 K/s:
✅ Sistema en estado estacionario
✅ Se genera el gráfico en ese instante
✅ Se guarda el resultado

---

## ⚠️ Notas Importantes

### 1. Tiempo de Simulación
- La simulación física puede alcanzar convergencia entre 20-60 segundos
- El tiempo real de ejecución depende del hardware (~5-10 minutos)

### 2. Diferencia con Gráfico Rápido
```
Gráfico Rápido (t=5s):
  ❌ Sistema todavía transitorio
  ❌ Temperaturas aún cambiando
  ❌ NO representa capacidad final del sistema

Gráfico en Convergencia (t=XX s):
  ✅ Sistema estacionario
  ✅ Temperaturas estables
  ✅ Representa capacidad final del sistema
```

### 3. Por Qué Tarda
- 120,000 pasos temporales posibles (0.5 ms cada uno)
- 1,860 nodos totales (cada uno debe converger)
- Cálculo de balance energético en cada paso
- Sistema con múltiples escalas temporales

---

## 🚀 Qué Hacer Ahora

### Opción A: Esperar (Recomendado)
```bash
# Monitorear cada ~2 minutos
./monitorear_convergencia.sh

# O ver en tiempo real
tail -f convergencia_output.log
```

### Opción B: Usar Gráfico Rápido Temporal
```bash
# Ya está disponible:
open resultados/figuras/distribucion_espacial_rapido_Al_t5.00s.png

# O en Linux:
xdg-open resultados/figuras/distribucion_espacial_rapido_Al_t5.00s.png
```

### Opción C: Detener y Reconfigurar
```bash
# Detener simulación
pkill -f generar_grafico_convergencia.py

# Editar script para t_max más corto o epsilon más grande
# Luego volver a ejecutar
```

---

## 📊 Cuando Termine

El script imprimirá automáticamente:

```
======================================================================
✅ GRÁFICOS GENERADOS EXITOSAMENTE
======================================================================

📊 Figuras guardadas:
   1. resultados/figuras/distribucion_espacial_convergencia_Al_tXX.XXs.png
   2. resultados/figuras/distribucion_espacial_final_Al_tYY.YYs.png

🌡️ Temperaturas en convergencia (t=XX.XXs):
   - Fluido: XX.X °C
   - Placa: XX.X °C
   - Aletas: XX.X °C

🌡️ Temperaturas al tiempo final (t=YY.YYs):
   - Fluido: YY.Y °C
   - Placa: YY.Y °C
   - Aletas: YY.Y °C

📈 Cambio después de convergencia:
   - Fluido: X.XX °C
   - Placa: X.XX °C
   - Aletas: X.XX °C
```

---

## 🔧 Troubleshooting

### "La simulación está tomando demasiado tiempo"

**Solución 1**: Relajar criterio de convergencia
```python
# En generar_grafico_convergencia.py, línea 52
epsilon = 5e-3  # Era 1e-3, ahora 5x más tolerante
```

**Solución 2**: Reducir tiempo máximo
```python
# En generar_grafico_convergencia.py, línea 50
t_max = 30.0  # Era 60.0, ahora 30s
```

### "Quiero cancelar la simulación"

```bash
pkill -f generar_grafico_convergencia.py
```

### "¿Cómo veo el resultado cuando termine?"

```bash
# Ejecutar el monitor
./monitorear_convergencia.sh

# Si muestra "Simulación no está corriendo", habrá terminado
# y mostrará automáticamente el resultado final
```

---

## 📚 Referencias

- **Script principal**: `generar_grafico_convergencia.py`
- **Script rápido**: `generar_grafico_rapido.py`
- **Monitor**: `monitorear_convergencia.sh`
- **Log**: `convergencia_output.log`
- **Función**: `graficar_distribucion_espacial_completa()` en `src/visualizacion.py`

---

**Última actualización**: En progreso
**Estado**: Simulación corriendo en segundo plano
**ETA**: 5-10 minutos desde el inicio

---

💡 **Tip**: Mientras esperas, puedes revisar el gráfico rápido generado para tener una idea preliminar de la distribución espacial del sistema.
