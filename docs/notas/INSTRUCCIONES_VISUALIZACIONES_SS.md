# 📊 INSTRUCCIONES: Visualizaciones Acero Inoxidable (SS)

---

## 🔄 Estado Actual

**Simulación de SS:** ⏳ EN EJECUCIÓN (iniciada a las 16:50 aprox.)

**Progreso:** ~18% completado (11s de 60s)

**Tiempo estimado restante:** 5-8 minutos

---

## ✅ Cuando la Simulación Complete

### 1️⃣ **Verificar que completó:**

```bash
./monitorear_simulacion_SS.sh
```

**Buscar este mensaje:**
```
✅ SIMULACIÓN COMPLETADA
🌡️  Temperaturas finales (t=60s):
```

**O verificar que el archivo existe:**
```bash
ls -lh resultados/datos/resultados_Stainless_Steel.npz
```

---

### 2️⃣ **Generar TODAS las visualizaciones:**

**Comando único:**
```bash
python3 generar_visualizaciones_SS.py
```

**Esto generará automáticamente 11 figuras:**

#### Figuras Individuales (3):
1. `balance_energetico_SS.png`
2. `evolucion_temporal_SS.png`
3. `convergencia_SS.png`

#### Figuras en t≈5s (3):
4. `perfiles_espaciales_SS_t5.00s.png`
5. `campos_2d_SS_t5.00s.png`
6. `distribucion_espacial_SS_t5.00s.png`

#### Figuras en t≈60s (3):
7. `perfiles_espaciales_SS_t60.00s.png`
8. `campos_2d_SS_t60.00s.png`
9. `distribucion_espacial_SS_t60.00s.png`

**Tiempo de generación:** ~2-3 minutos

---

### 3️⃣ **Verificar que se generaron:**

```bash
ls -lh resultados/figuras/*_SS*.png
```

**Deberías ver 9 archivos nuevos** (algunas funciones pueden generar más de una figura)

---

## 📊 Comparación Al vs SS

### Figuras que tendrás para comparar:

| Tipo de Gráfico | Aluminio | Acero Inoxidable |
|------------------|----------|------------------|
| **Balance energético** | ✅ balance_energetico_Al.png | ⏳ balance_energetico_SS.png |
| **Evolución temporal** | ✅ evolucion_temporal_Al.png | ⏳ evolucion_temporal_SS.png |
| **Convergencia** | ✅ convergencia_Al.png | ⏳ convergencia_SS.png |
| **Perfiles @ t=5s** | ✅ perfiles_espaciales_Al_t5.00s.png | ⏳ perfiles_espaciales_SS_t5.00s.png |
| **Perfiles @ t=60s** | ✅ perfiles_espaciales_Al_t60.00s.png | ⏳ perfiles_espaciales_SS_t60.00s.png |
| **Campos 2D @ t=5s** | ✅ campos_2d_Al_t5.00s.png | ⏳ campos_2d_SS_t5.00s.png |
| **Campos 2D @ t=60s** | ✅ campos_2d_Al_t60.00s.png | ⏳ campos_2d_SS_t60.00s.png |
| **Distribución @ t=5s** | ✅ distribucion_espacial_Al_t5.00s.png | ⏳ distribucion_espacial_SS_t5.00s.png |
| **Distribución @ t=60s** | ✅ distribucion_espacial_Al_t60.00s.png | ⏳ distribucion_espacial_SS_t60.00s.png |

**Total:** 18 figuras (9 Al + 9 SS)

---

## 🔍 Monitorear Progreso

### Ver progreso actual:
```bash
./monitorear_simulacion_SS.sh
```

### Ver progreso en tiempo real:
```bash
tail -f simulacion_SS.log
# Presiona Ctrl+C para salir
```

### Ver últimas 50 líneas:
```bash
tail -n 50 simulacion_SS.log
```

---

## 📈 Progreso Esperado

**Evolución de max|dT/dt| para SS:**

| Tiempo | max\|dT/dt\| | Estado |
|--------|-------------|--------|
| 0s | ~12,000 K/s | Inicial |
| 10s | ~0.7 K/s | Transitorio lento |
| 30s | ~0.5 K/s | Acercándose |
| 60s | ~0.3 K/s | Cercano (pero no convergido) |

**Nota:** SS tarda ~20× más que Al, por lo que no alcanzará convergencia total en 60s (esperado).

---

## 🌡️ Temperaturas Esperadas

### Aluminio @ t=60s (referencia):
- Fluido: 79.9°C
- Placa: 66.2°C
- Aletas: 66.1°C

### Acero Inoxidable @ t=60s (estimado):
- Fluido: ~79.9°C (igual, dominado por advección)
- Placa: ~40-45°C (mucho más frío que Al)
- Aletas: ~38-43°C (mucho más frío que Al)

**Razón:** SS tiene α = 4.05×10⁻⁶ m²/s (20× menor que Al), por lo que difunde calor mucho más lento.

---

## ⚠️ Si Algo Sale Mal

### Error: "archivo no encontrado"
```bash
# Verificar que la simulación completó
ls -lh resultados/datos/resultados_Stainless_Steel.npz

# Si no existe, revisar el log
tail -n 100 simulacion_SS.log
```

### Error en generar_visualizaciones_SS.py
```bash
# Ver el error completo
python3 generar_visualizaciones_SS.py 2>&1 | tee error_visualizaciones.log
```

### La simulación se detuvo
```bash
# Verificar si el proceso está corriendo
pgrep -f "simular_acero.py"

# Si no está corriendo, revisar qué pasó
tail -n 50 simulacion_SS.log

# Reiniciar si es necesario
nohup python3 simular_acero.py > simulacion_SS.log 2>&1 &
```

---

## 💡 Después de Generar las Visualizaciones

### Comparar visualmente Al vs SS:

**En tu visor de imágenes favorito, abrir lado a lado:**

1. **Evolución temporal:**
   - `evolucion_temporal_Al.png` vs `evolucion_temporal_SS.png`
   - **Observar:** Curvas de Al suben más rápido

2. **Distribución espacial @ t=60s:**
   - `distribucion_espacial_Al_t60.00s.png` vs `distribucion_espacial_SS_t60.00s.png`
   - **Observar:** Al tiene colores más cálidos (más cerca del agua)

3. **Convergencia:**
   - `convergencia_Al.png` vs `convergencia_SS.png`
   - **Observar:** Al converge más rápido

---

## 📝 Análisis Sugerido

### Pregúntate:

1. **¿Cuánto más lento es SS que Al?**
   - Comparar temperaturas a t=60s
   - Comparar pendientes en evolución temporal

2. **¿Los gradientes en SS son mayores?**
   - Comparar perfiles espaciales
   - SS debería mostrar más variación (Bi_SS = 3.13 > Bi_Al = 0.21)

3. **¿El balance energético es similar?**
   - Comparar Q_in, Q_out, error
   - Forma de las curvas debería ser similar, pero magnitudes diferentes

4. **¿La distribución espacial muestra diferencias?**
   - En SS, ¿la placa tiene mayor gradiente vertical?
   - En SS, ¿las aletas están más frías en el centro?

---

## ✅ Checklist Final

- [ ] Simulación SS completada (verificar con `monitorear_simulacion_SS.sh`)
- [ ] Archivo `resultados_Stainless_Steel.npz` existe
- [ ] Ejecutar `python3 generar_visualizaciones_SS.py`
- [ ] Verificar que se generaron 9 figuras de SS
- [ ] Comparar visualmente Al vs SS
- [ ] Listo para presentación con ambos materiales ✅

---

**Creado:** 2025-10-05  
**Última actualización:** Esperando simulación SS...  
**Status:** ⏳ Simulación en progreso (~5-8 min restantes)
