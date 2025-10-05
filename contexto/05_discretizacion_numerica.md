# Discretización Numérica y Mallas

## 1. Estrategia General de Discretización

### Dominios a Discretizar
1. **Fluido (1D)**: Discretización en dirección x
2. **Placa (2D)**: Discretización en plano x-y (cartesiano)
3. **Aletas (2D × 3)**: Discretización en plano r-θ (cilíndrico) para cada una de las 3 aletas

### Notas Importantes
- **NO hay periodicidad**: El fluido cambia de temperatura a lo largo de x
- **Resolver todo el sistema completo**: 3 módulos (aletas) en serie
- El parámetro W (ancho) solo se usa para cálculos de área, NO se discretiza

---

## 2. Especificaciones de Mallas

### Malla del Fluido (1D)

| Parámetro | Valor |
|-----------|-------|
| Extensión x | 0 ≤ x ≤ 0.03 m |
| Número de nodos | 60 |
| Espaciamiento | $\Delta x = 0.03/59 \approx 5.08 \times 10^{-4}$ m = 0.508 mm |

**Notación:**
- Índice: $i = 0, 1, 2, ..., 59$
- Posición: $x_i = i \cdot \Delta x$

### Malla de la Placa (2D Cartesiano)

| Parámetro | Valor |
|-----------|-------|
| Extensión x | 0 ≤ x ≤ 0.03 m |
| Extensión y | 0 ≤ y ≤ 0.01 m |
| Nodos en x | 60 |
| Nodos en y | 20 |
| Espaciamiento x | $\Delta x \approx 5.08 \times 10^{-4}$ m = 0.508 mm |
| Espaciamiento y | $\Delta y = 0.01/19 \approx 5.26 \times 10^{-4}$ m = 0.526 mm |

**Notación:**
- Índices: $i = 0, 1, ..., 59$ (eje x), $j = 0, 1, ..., 19$ (eje y)
- Posición: $(x_i, y_j) = (i \cdot \Delta x, j \cdot \Delta y)$
- $j=0$ corresponde a la interfaz agua-placa
- $j=19$ corresponde a la superficie superior (aire)

### Malla de las Aletas (2D Cilíndrico, k=1,2,3)

| Parámetro | Valor |
|-----------|-------|
| Extensión radial | 0 ≤ r ≤ 0.004 m |
| Extensión angular | 0 ≤ θ ≤ π rad |
| Nodos en r | 10 |
| Nodos en θ | 20 |
| Espaciamiento r | $\Delta r = 0.004/9 \approx 4.44 \times 10^{-4}$ m = 0.444 mm |
| Espaciamiento θ | $\Delta \theta = \pi/19 \approx 0.165$ rad = 9.47° |

**Notación (para cada aleta k):**
- Índices: $j = 0, 1, ..., 9$ (eje r), $m = 0, 1, ..., 19$ (eje θ)
- Posición: $(r_j, \theta_m) = (j \cdot \Delta r, m \cdot \Delta \theta)$
- $j=0$ es el centro (r=0, con tratamiento especial)
- $j=9$ es la superficie (r=R, condición de convección)
- $m=0$ y $m=19$ son los bordes planos (interfaz con placa)

**Centros de las aletas (eje x):**
- Aleta 1: $x_1 = 0.005$ m (i ≈ 10)
- Aleta 2: $x_2 = 0.015$ m (i ≈ 30)
- Aleta 3: $x_3 = 0.025$ m (i ≈ 49)

---

## 3. Paso de Tiempo y Estabilidad

### Restricciones de Estabilidad

#### Criterio CFL (Fluido)
Para el esquema explícito de advección:

$$CFL = \frac{u \Delta t}{\Delta x} \leq 1$$

$$\Delta t \leq \frac{\Delta x}{u} = \frac{5.08 \times 10^{-4}}{0.111} \approx 4.58 \times 10^{-3} \text{ s}$$

#### Criterio de Fourier (Placa - Aluminio)
Para estabilidad en 2D con FTCS:

$$Fo_x + Fo_y = \frac{\alpha \Delta t}{\Delta x^2} + \frac{\alpha \Delta t}{\Delta y^2} \leq 0.5$$

Para Aluminio ($\alpha_{Al} = 6.87 \times 10^{-5}$ m²/s):

$$\Delta t \leq \frac{0.5}{\alpha_{Al} \left(\frac{1}{\Delta x^2} + \frac{1}{\Delta y^2}\right)} = \frac{0.5}{6.87 \times 10^{-5} \left(\frac{1}{(5.08 \times 10^{-4})^2} + \frac{1}{(5.26 \times 10^{-4})^2}\right)}$$

$$\Delta t \leq 9.27 \times 10^{-4} \text{ s (Aluminio)}$$

Para Acero Inoxidable ($\alpha_{SS} = 4.05 \times 10^{-6}$ m²/s):

$$\Delta t \leq 1.57 \times 10^{-2} \text{ s (Acero Inoxidable)}$$

#### Criterio de Fourier (Aletas)

Para coordenadas cilíndricas, considerando $\Delta r$ y $r \Delta \theta$:

$$Fo_r + Fo_\theta = \frac{\alpha \Delta t}{\Delta r^2} + \frac{\alpha \Delta t}{(r \Delta \theta)^2} \leq 0.5$$

El término más restrictivo ocurre en $r = R = 0.004$ m:

Para Aluminio:
$$\Delta t \leq 1.28 \times 10^{-3} \text{ s}$$

### Paso de Tiempo Recomendado

Tomando el criterio más restrictivo (Aluminio en la placa):

$$\boxed{\Delta t = 5.0 \times 10^{-4} \text{ s} = 0.5 \text{ ms}}$$

**Verificación:**
- CFL: $0.111 \times 5 \times 10^{-4} / 5.08 \times 10^{-4} = 0.109$ ✓
- Fourier Al (placa): $6.87 \times 10^{-5} \times 5 \times 10^{-4} \times (1/(5.08 \times 10^{-4})^2 + 1/(5.26 \times 10^{-4})^2) = 0.27$ ✓
- Fourier SS (placa): mucho menor ✓

---

## 4. Esquemas Numéricos

### 4.1 Fluido - Upwind + Euler Explícito

**Ecuación discreta:**

$$T_{f,i}^{n+1} = T_{f,i}^n - CFL(T_{f,i}^n - T_{f,i-1}^n) - \gamma \Delta t (T_{f,i}^n - T_{s,i}^n)$$

**Donde:**
- $CFL = \frac{u \Delta t}{\Delta x}$
- $T_{s,i}^n$: Temperatura de la placa en $(x_i, y=0)$ en el tiempo $n$
- Upwind hacia $i-1$ porque $u > 0$

**Condiciones de frontera:**
- Entrada ($i=0$): $T_{f,0}^{n+1} = 80°C$ (Dirichlet)
- Salida ($i=59$): $T_{f,59}^{n+1} = T_{f,58}^{n+1}$ (extrapolación de orden 0)

### 4.2 Placa - FTCS Explícito

**Ecuación discreta:**

$$T_{i,j}^{n+1} = T_{i,j}^n + Fo_x(T_{i+1,j}^n - 2T_{i,j}^n + T_{i-1,j}^n) + Fo_y(T_{i,j+1}^n - 2T_{i,j}^n + T_{i,j-1}^n)$$

**Donde:**
- $Fo_x = \frac{\alpha \Delta t}{\Delta x^2}$
- $Fo_y = \frac{\alpha \Delta t}{\Delta y^2}$

**Nodos internos:** $i = 1, ..., 58$ y $j = 1, ..., 18$

### 4.3 Condiciones de Robin Discretas (Nodos Fantasma)

#### Interfaz Agua-Placa (j=0)

Condición: $-k_s \frac{\partial T}{\partial y}\Big|_{y=0} = h_{agua}(T_{i,0} - T_{f,i})$

Aproximación de derivada con nodo fantasma $T_{i,-1}$:

$$-k_s \frac{T_{i,1} - T_{i,-1}}{2\Delta y} = h_{agua}(T_{i,0} - T_{f,i})$$

Despejando el nodo fantasma:

$$T_{i,-1} = T_{i,1} - \frac{2 h_{agua} \Delta y}{k_s}(T_{i,0} - T_{f,i})$$

Sustituyendo en la ecuación de FTCS para $j=0$:

$$T_{i,0}^{n+1} = T_{i,0}^n + Fo_x(T_{i+1,0}^n - 2T_{i,0}^n + T_{i-1,0}^n) + 2Fo_y\left[(T_{i,1}^n - T_{i,0}^n) - \frac{h_{agua} \Delta y}{k_s}(T_{i,0}^n - T_{f,i}^n)\right]$$

#### Superficie Superior - Aire (j=Ny=19)

Condición: $-k_s \frac{\partial T}{\partial y}\Big|_{y=e_{base}} = h_{aire}(T_{i,Ny} - T_\infty)$

Nodo fantasma $T_{i,Ny+1}$:

$$T_{i,Ny+1} = T_{i,Ny} + \frac{2 h_{aire} \Delta y}{k_s}(T_{i,Ny} - T_\infty)$$

Ecuación para $j=Ny$:

$$T_{i,Ny}^{n+1} = T_{i,Ny}^n + Fo_x(T_{i+1,Ny}^n - 2T_{i,Ny}^n + T_{i-1,Ny}^n) + 2Fo_y\left[(T_{i,Ny-1}^n - T_{i,Ny}^n) + \frac{h_{aire} \Delta y}{k_s}(T_{i,Ny}^n - T_\infty)\right]$$

### 4.4 Aletas - FTCS Cilíndrico

#### Para r > 0 (j = 1, ..., 8)

$$T_{j,m}^{n+1} = T_{j,m}^n + Fo_r \left[ (T_{j+1,m}^n - 2T_{j,m}^n + T_{j-1,m}^n) + \frac{\Delta r}{r_j}(T_{j+1,m}^n - T_{j-1,m}^n) \right] + Fo_\theta \frac{1}{r_j^2}(T_{j,m+1}^n - 2T_{j,m}^n + T_{j,m-1}^n)$$

**Donde:**
- $Fo_r = \frac{\alpha \Delta t}{\Delta r^2}$
- $Fo_\theta = \alpha \Delta t$
- $r_j = j \cdot \Delta r$

#### Para r = 0 (j = 0) - Simetría con L'Hôpital

Aplicando la regla de L'Hôpital para el término singular:

$$T_{0,m}^{n+1} = T_{0,m}^n + 2Fo_r (T_{1,m}^n - T_{0,m}^n)$$

**Nota:** En el centro, la temperatura es independiente de θ por simetría.

#### Superficie r = R (j = Nr = 9) - Convección con Aire

Nodo fantasma $T_{Nr+1,m}$:

$$T_{Nr+1,m} = T_{Nr,m} + \frac{2 h_{aire} \Delta r}{k_s}(T_{Nr,m} - T_\infty)$$

Ecuación:

$$T_{Nr,m}^{n+1} = T_{Nr,m}^n + 2Fo_r \left[ (T_{Nr-1,m}^n - T_{Nr,m}^n) + \frac{h_{aire} \Delta r}{k_s}(T_{Nr,m}^n - T_\infty) \right] + Fo_\theta \frac{1}{R^2}(T_{Nr,m+1}^n - 2T_{Nr,m}^n + T_{Nr,m-1}^n)$$

---

## 5. Acoplamiento Placa-Aleta

### Continuidad en la Interfaz

Para cada aleta k en las posiciones angulares $\theta = 0$ (m=0) y $\theta = \pi$ (m=19):

**Mapeo de coordenadas:**
- Aleta: $(r_j, \theta_m)$ con $m = 0$ o $19$
- Placa: $(x, y) = (x_k \pm r_j \cos(\theta_m), e_{base})$

**Interpolación:**
1. Calcular la posición cartesiana del nodo de la aleta
2. Interpolar bilinealmente desde la malla de la placa
3. Igualar temperaturas

**Continuidad de flujo:**
El flujo radial en la aleta debe igualar el flujo vertical en la placa.

---

## 6. Algoritmo de Solución Temporal

```
INICIALIZACIÓN:
  T_placa = T_aletas = 23°C
  T_fluido calculado desde la entrada (perfil inicial)
  
BUCLE TEMPORAL (n = 0, 1, 2, ...):
  
  1. ACTUALIZAR FLUIDO:
     Para i = 1 a Nx-1:
       Extraer T_s,i desde placa en j=0
       Aplicar upwind + acople: T_f,i(n+1)
     
  2. ACTUALIZAR PLACA:
     Para i = 1 a Nx-2, j = 0 a Ny:
       Si j=0: aplicar BC de agua
       Si j=Ny: aplicar BC de aire
       Sino: FTCS estándar
       
  3. ACTUALIZAR ALETAS (para k=1,2,3):
     Para j = 0 a Nr, m = 0 a Nθ:
       Si j=0: tratamiento de simetría
       Si j=Nr: BC de aire
       Si m=0 o m=Nθ: aplicar continuidad con placa
       Sino: FTCS cilíndrico
       
  4. VERIFICAR CONVERGENCIA:
     Si cambio < tolerancia → ESTADO ESTACIONARIO
     
  5. n = n + 1
  
FIN BUCLE
```

---

## 7. Consideraciones Numéricas

### Precisión
- Esquema FTCS: O(Δt, Δx², Δy², Δr², Δθ²)
- Upwind: O(Δt, Δx)

### Estabilidad
- Respetar límites CFL y Fourier
- Verificar en cada paso si se mantienen las restricciones

### Conservación
- Verificar balance energético global periódicamente
- Errores de interpolación pueden acumularse

### Paralelización
- Cada aleta puede actualizarse en paralelo
- El fluido debe procesarse secuencialmente (upwind)

---

## Resumen de Números de Malla

| Dominio | Nodos | Total |
|---------|-------|-------|
| Fluido | 60 | 60 |
| Placa | 60 × 20 | 1,200 |
| Aleta 1 | 10 × 20 | 200 |
| Aleta 2 | 10 × 20 | 200 |
| Aleta 3 | 10 × 20 | 200 |
| **TOTAL** | - | **1,860 nodos** |

---

## Notas para Implementación en Python

1. Usar NumPy arrays para todas las mallas
2. Pre-calcular coeficientes Fo_x, Fo_y, Fo_r, Fo_θ, CFL
3. Implementar función de interpolación bilineal para interfaz placa-aleta
4. Almacenar historial de temperatura para análisis de convergencia
5. Graficar perfiles cada N pasos de tiempo
