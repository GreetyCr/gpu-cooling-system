# Parámetros del Sistema

## Tabla I: Geometría

| Parámetro | Símbolo | Valor | Unidades | Expresión/Fuente |
|-----------|---------|-------|----------|------------------|
| Longitud en dirección del flujo | $L_x$ | 0.03 | m | Dado por proyecto (10 cm total en figura, 3 cm por módulo) |
| Ancho/profundidad (eje z) | $W$ | 0.10 | m | Figura 1 - longitud del dispositivo |
| Espesor placa base | $e_{base}$ | 0.01 | m | Figura 1 - 1.0 cm de espesor placa |
| Claro hidráulico canal | $e_{agua}$ | 0.003 | m | Figura 1 - 0.3 cm canal de refrigerante |
| Diámetro de domos | $D$ | 0.008 | m | Figura 1 - diámetro = 0.8 cm |
| Radio de domos | $r$ | 0.004 | m | Calculado: $r = D/2$ |
| Paso entre domos | $p$ | 0.010 | m | Figura 1 - 1.0 cm de separación centro a centro |
| Separación plana | $s$ | 0.002 | m | Calculado: $s = p - D = 1.0 - 0.8 = 0.2$ cm |
| Número de domos | $N$ | 3 | adimensional | Figura 1 - muestra 3 domos semicirculares |

### Nota Geométrica
- **Altura geométrica total expuesta al aire**: $(e_{base} + r) = 0.014$ m
- **Posiciones de los centros de aletas** (eje x):
  - Aleta 1: $x_1 = 0.005$ m
  - Aleta 2: $x_2 = 0.015$ m
  - Aleta 3: $x_3 = 0.025$ m

---

## Tabla II: Parámetros de Operación

| Parámetro | Símbolo | Valor | Unidades | Expresión/Fuente |
|-----------|---------|-------|----------|------------------|
| Caudal de agua | $Q$ | 3.33×10⁻⁵ | m³/s | Investigado - valor típico en sistemas GPU (Koolance, 2025) - equivalente a 2 L/min |
| Velocidad media agua | $u$ | 0.111 | m/s | Calculado: $u = Q/A_c = 3.33×10^{-5}/(3.0×10^{-4})$ |
| Coeficiente convectivo agua | $h_{agua}$ | 600 | W·m⁻²·K⁻¹ | Investigado - criterio ingenieril para interfaz agua-metal (The Engineering ToolBox, 2003) |
| Coeficiente convectivo aire | $h_{aire}$ | 10 | W·m⁻²·K⁻¹ | Investigado - convección natural aire-metal (The Engineering ToolBox, 2003) |

### Condiciones de Temperatura
- **Temperatura aire ambiente**: $T_\infty = 23$ °C = 296.15 K (Supuesto - condición ambiental)
- **Temperatura inicial sólido**: $T_{inicial} = 23$ °C = 296.15 K (Supuesto - equilibrio inicial con ambiente)
- **Temperatura entrada agua (inicial)**: $T_{f,in,0} = 50$ °C = 323.15 K (Enunciado - temperatura antes del cambio)
- **Temperatura entrada agua (nueva)**: $T_{f,in} = 80$ °C = 353.15 K (Enunciado - temperatura después del cambio)

---

## Tabla III: Propiedades Termofísicas del Agua

| Parámetro | Símbolo | Valor | Unidades | Nota |
|-----------|---------|-------|----------|------|
| Conductividad térmica | $k_w$ | 0.563 | W·m⁻¹·K⁻¹ | Investigado - evaluado a temperatura promedio (~65°C) |
| Densidad | $\rho_{agua}$ | 980.5 | kg·m⁻³ | Investigado - evaluado a temperatura promedio (~65°C) |
| Calor específico | $c_{p,agua}$ | 4180 | J·kg⁻¹·K⁻¹ | Investigado - evaluado a temperatura promedio (~65°C) |

**Nota:** Las propiedades del agua se evalúan a la temperatura promedio entre entrada (80°C) y temperatura inicial (50°C) para mejor aproximación.

---

## Tabla IV: Propiedades Termofísicas - Aluminio 6061

| Parámetro | Símbolo | Valor | Unidades |
|-----------|---------|-------|----------|
| Conductividad térmica | $k_{Al}$ | 167 | W·m⁻¹·K⁻¹ |
| Densidad | $\rho_{Al}$ | 2700 | kg·m⁻³ |
| Calor específico | $c_{p,Al}$ | 900 | J·kg⁻¹·K⁻¹ |
| Difusividad térmica | $\alpha_{Al}$ | 6.87×10⁻⁵ | m²/s |

### Cálculo de difusividad térmica:
$\alpha_{Al} = \frac{k_{Al}}{\rho_{Al} \cdot c_{p,Al}} = \frac{167}{2700 \times 900} = 6.87 \times 10^{-5} \text{ m}^2/\text{s}$

**Fuente:** ASM (2019) - Aluminum 6061-T6; 6061-T651. Propiedades evaluadas a temperatura ambiente, consideradas constantes según supuestos del proyecto.

---

## Tabla V: Propiedades Termofísicas - Acero Inoxidable 304

| Parámetro | Símbolo | Valor | Unidades |
|-----------|---------|-------|----------|
| Conductividad térmica | $k_{SS}$ | 16.2 | W·m⁻¹·K⁻¹ |
| Densidad | $\rho_{SS}$ | 8000 | kg·m⁻³ |
| Calor específico | $c_{p,SS}$ | 500 | J·kg⁻¹·K⁻¹ |
| Difusividad térmica | $\alpha_{SS}$ | 4.05×10⁻⁶ | m²/s |

### Cálculo de difusividad térmica:
$\alpha_{SS} = \frac{k_{SS}}{\rho_{SS} \cdot c_{p,SS}} = \frac{16.2}{8000 \times 500} = 4.05 \times 10^{-6} \text{ m}^2/\text{s}$

**Fuente:** Aalco (2005) - Grade 304 Stainless Steel: Properties, Fabrication and Applications. Propiedades evaluadas a temperatura ambiente, consideradas constantes según supuestos del proyecto.

---

## Tabla VI: Parámetros Derivados

| Parámetro | Símbolo | Valor | Unidades | Expresión |
|-----------|---------|-------|----------|-----------|
| Área de flujo canal | $A_c$ | 3.0×10⁻⁴ | m² | $A_c = W \times e_{agua} = 0.10 \times 0.003$ |
| Diámetro hidráulico | $D_h$ | 0.006 | m | $D_h = 2 \times e_{agua}$ (canal rectangular muy ancho) |
| Perímetro de intercambio | $P_s$ | 0.10 | m | $P_s = W$ (solo superficie inferior del canal) |
| Longitud expuesta/domo | $l_{aire}$ | 0.01457 | m | $l_{aire} = \pi r + s = \pi(0.004) + 0.002$ |
| Área total expuesta al aire | $A_{aire}$ | 0.004371 | m² | $A_{aire} = l_{aire} \times W \times N = 0.01457 \times 0.10 \times 3$ |
| Parámetro de acople | $\gamma$ | 4.88×10⁻² | s⁻¹ | $\gamma = \frac{h_{agua}}{\rho_{agua} c_{p,agua} e_{agua}} = \frac{600}{980.5 \times 4180 \times 0.003}$ |

### Cálculo del parámetro de acople:
$\gamma = \frac{h_{agua}}{\rho_{agua} \cdot c_{p,agua} \cdot e_{agua}} = \frac{600}{980.5 \times 4180 \times 0.003} = 4.88 \times 10^{-2} \text{ s}^{-1}$

Este parámetro caracteriza la intensidad del acoplamiento térmico entre el fluido y el sólido. Un valor mayor implica un intercambio térmico más rápido entre el agua y la placa.

---

## Notas Importantes para Implementación

1. **Unidades**: Todos los parámetros están en SI. Mantener consistencia en todo el código.

2. **Constantes derivadas**: Los parámetros de la Tabla VI deben calcularse a partir de los parámetros base.

3. **Selección de material**: El código debe poder cambiar fácilmente entre Aluminio y Acero Inoxidable modificando solo las propiedades $k$, $\rho$, $c_p$, y $\alpha$.

4. **Temperaturas**: Usar Kelvin en todos los cálculos para evitar errores.

5. **Diferencia de difusividades**: 
   - $\alpha_{Al} / \alpha_{SS} \approx 17$
   - El aluminio responde ~17 veces más rápido que el acero inoxidable

---

## Fuentes Bibliográficas

### Referencias Citadas

**ASM (2019).** Aluminum 6061-T6 ; 6061-T651. ASM Material Data Sheet. Recuperado de: https://asm.matweb.com/search/specificmaterial.asp?bassnum=ma6061t6

**Aalco (2005).** Grade 304 Stainless Steel: Properties, Fabrication and Applications. AZO Materials. Recuperado de: https://www.azom.com/article.aspx?ArticleID=2867

**The Engineering ToolBox (2003).** Understanding Convective Heat Transfer: Coefficients, Formulas & Examples. Recuperado de: https://www.engineeringtoolbox.com/convective-heat-transfer-d_430.html

**Koolance (2025).** How To Build A Water Cooled PC. Koolance Technical Guide. Recuperado de: https://koolance.com/how-to-build-a-water-cooled-pc

### Notas sobre las Fuentes

- **Propiedades de materiales** (Al 6061, SS 304): Tomadas de bases de datos estándar de ingeniería (ASM, Aalco).
- **Coeficientes convectivos**: Valores típicos de literatura de transferencia de calor para configuraciones similares.
- **Caudal de agua**: Investigado como valor representativo de sistemas comerciales de enfriamiento líquido para GPUs.
- **Propiedades del agua**: Evaluadas a temperatura promedio del rango de operación (~65°C).

### Supuestos Clave del Proyecto

1. **Aire siempre a 23°C**: Supuesto razonable para ambiente de laboratorio/oficina con control de temperatura.

2. **Temperatura inicial del sólido = 23°C**: Sistema en equilibrio térmico con el ambiente antes del cambio.

3. **Agua fluye constantemente con flujo fijo**: Simplificación válida para sistema con bomba de velocidad constante.

4. **Coeficientes convectivos constantes**: Aproximación aceptable dado que los números de Reynolds y Rayleigh no varían drásticamente.

5. **Problema 2D en plano x-y**: Justificado por condición de infinitud en dirección z (longitud >> diámetro).

6. **Contacto térmico perfecto**: Asume que la resistencia térmica de contacto es despreciable comparada con la conducción en el sólido.

7. **Propiedades independientes de temperatura**: Simplificación válida para el rango de temperaturas considerado (23-80°C).

8. **Sin generación de calor interna**: No hay disipación de energía dentro de los materiales.

9. **Radiación despreciable**: Válido porque las temperaturas son relativamente bajas (< 100°C) y los coeficientes convectivos dominan.

10. **Canal con paredes laterales e inferior adiabáticas**: Supone buen aislamiento en estas superficies, concentrando el intercambio en la interfaz agua-placa.
