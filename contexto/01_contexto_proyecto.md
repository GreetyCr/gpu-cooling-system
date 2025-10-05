# Contexto del Proyecto: Sistema de Enfriamiento Líquido para GPU

## Objetivo General
Calcular el tiempo que tarda un sistema de enfriamiento líquido para GPU en llegar al estado estacionario luego de un cambio en la temperatura del agua (de 50 °C a 80 °C) utilizando dos materiales distintos: **Aluminio (Al)** y **Acero Inoxidable (SS)**.

Desarrollar un criterio técnica y termodinámicamente sustentado para definir el equilibrio.

## Descripción del Sistema

### Geometría
- **Placa base rectangular** con superficie expandida (aletas semicirculares)
- **3 aletas semicirculares** (domos) en la parte superior
- **Canal de agua** en la parte inferior de la placa
- El agua fluye en dirección axial (eje x) a través del canal
- Aire ambiente rodea las superficies superiores

### Configuración Geométrica
```
Aire a 23°C (superior)
    ↓
[Aleta1] [Aleta2] [Aleta3]  ← Domos semicirculares (D=0.8 cm)
─────────────────────────────  ← Placa base (1.0 cm espesor)
═════════════════════════════  ← Canal de agua (0.3 cm)
    → Flujo de agua
```

## Suposiciones del Modelo

### Suposiciones Ambientales
1. **Aire ambiente**: Temperatura constante a 23 °C en todo momento
2. **Temperatura inicial del sólido**: 23 °C uniforme (igual a la temperatura del aire)

### Suposiciones del Fluido
3. **Temperatura de entrada del agua**:
   - Inicialmente: 50 °C (retira energía de la GPU)
   - Cambio en t=0: 80 °C (nuevo régimen)
4. **Caudal constante**: 2.0 L/min = 3.33×10⁻⁵ m³/s (valor típico en sistemas de enfriamiento líquido de GPUs)

### Suposiciones de Transferencia de Calor
5. **Coeficientes convectivos constantes**:
   - Agua-placa: h_agua = 600 W·m⁻²·K⁻¹
   - Aire-superficie: h_aire = 10 W·m⁻²·K⁻¹
6. **Radiación**: Despreciable (no se considera)
7. **Contacto térmico perfecto**: En todas las interfaces internas (placa-aleta)
   - Continuidad de temperatura
   - Continuidad de flujo de calor normal

### Suposiciones Geométricas y Dimensionales
8. **Problema 2D**: La transferencia de calor no varía con el eje z (profundidad/ancho)
   - Justificación: Sistema "infinito" en dirección z (mucho más largo que su diámetro)
   - Reduce el problema al plano x-y
9. **Canal de agua**: 
   - Claro hidráulico: 0.003 m
   - Paredes laterales e inferior: **adiabáticas** (no hay transferencia de calor)

### Suposiciones de Propiedades
10. **Propiedades termofísicas constantes**: No dependen de la temperatura
    - Aluminio 6061
    - Acero inoxidable 304
    - Agua
11. **Sin generación de calor interna**: No hay fuentes de calor dentro del sólido

## Comparación de Materiales
El análisis se realizará para dos casos:
- **Caso 1**: Sistema construido en Aluminio 6061
- **Caso 2**: Sistema construido en Acero Inoxidable 304

Se compararán:
- Tiempo de respuesta al cambio de temperatura
- Distribución de temperatura en estado transitorio
- Eficiencia de disipación de calor
- Criterio de estado estacionario

## Sistema de Coordenadas

### Ejes
- **Eje x**: Dirección del flujo de agua (0 ≤ x ≤ 0.03 m)
- **Eje y**: Espesor vertical (0 = interfaz agua, y_max = superficie aire)
- **Eje z**: Profundidad/ancho (0 ≤ z ≤ 0.10 m) - **No discretizado, solo para cálculos de área**

### Dominios
1. **Fluido (agua)**: Modelo 1D convectivo en dirección x
2. **Placa base**: Modelo 2D cartesiano (x-y)
3. **Aletas semicirculares**: Modelo 2D cilíndrico (r-θ)

## Criterio de Estado Estacionario
Se debe desarrollar un criterio cuantitativo para determinar cuándo el sistema ha alcanzado el equilibrio térmico, considerando:
- Cambio relativo de temperatura en el tiempo
- Distribución espacial de temperatura
- Balance energético global
