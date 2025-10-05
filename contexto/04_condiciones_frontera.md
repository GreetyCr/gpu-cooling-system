# Condiciones de Frontera e Interfaz

## 1. Condiciones Iniciales (t=0)

### Sólido (Placa y Aletas)
Temperatura inicial uniforme igual a la temperatura ambiente:

$$T(x,y,0) = T_\infty = 23°C = 296.15 \text{ K}$$

**Aplicable a:**
- Toda la placa base: $\forall (x,y) \in [0, L_x] \times [0, e_{base}]$
- Todas las aletas: $\forall (r,\theta) \in [0, R] \times [0, \pi]$, para k=1,2,3

### Fluido
La temperatura del fluido en $t=0^-$ estaba en régimen con $T_{f,in} = 50°C$.
En $t=0^+$ cambia a:

$$T_f(0,t) = 80°C = 353.15 \text{ K}, \quad \forall t > 0$$

---

## 2. Condiciones de Frontera - Fluido (Agua)

### Entrada del Canal (x=0)
Condición de Dirichlet (temperatura prescrita):

$$T_f(0,t) = T_{f,in} = 80°C = 353.15 \text{ K}$$

**Nota:** Esta es la condición que genera el transitorio al cambiar desde 50°C.

### Salida del Canal (x=Lx)
Condición de salida convectiva (Neumann de flujo nulo):

$$\left. \frac{\partial T_f}{\partial x} \right|_{x=L_x} = 0$$

**Interpretación:** Permite que el fluido salga del dominio sin reflexiones numéricas. NO implica que $T_f$ sea constante en el dominio, solo que la derivada espacial es cero en la salida.

---

## 3. Condiciones de Frontera - Placa Base

### Interfaz Agua-Placa (y=0)
Condición de Robin (convección):

$$-k_s \left. \frac{\partial T}{\partial y} \right|_{y=0} = h_{agua} (T_s - T_f)$$

**Donde:**
- $k_s$: Conductividad térmica del sólido (Al o SS)
- $T_s = T(x,0,t)$: Temperatura de la superficie de la placa
- $T_f = T_f(x,t)$: Temperatura del fluido en esa posición x
- $h_{agua} = 600$ W·m⁻²·K⁻¹

**Interpretación:** El flujo de calor conductivo en el sólido iguala el flujo convectivo hacia/desde el fluido.

### Superficie Superior - Zonas Planas (y=ebase)
Condición de Robin (convección con aire):

$$-k_s \left. \frac{\partial T}{\partial y} \right|_{y=e_{base}} = h_{aire} (T_s - T_\infty)$$

**Donde:**
- $T_\infty = 23°C = 296.15$ K: Temperatura del aire ambiente
- $h_{aire} = 10$ W·m⁻²·K⁻¹

**Región de aplicación:** Solo en las zonas de la superficie superior donde NO hay aletas (entre domos).

### Paredes Laterales (x=0 y x=Lx)
Condición de periodicidad o simetría (según el contexto):

Para simplificar, asumimos simetría en los extremos:

$$\left. \frac{\partial T}{\partial x} \right|_{x=0} = 0, \quad \left. \frac{\partial T}{\partial x} \right|_{x=L_x} = 0$$

**Nota:** Esto es una aproximación. En la práctica, puede haber gradientes cerca de los extremos.

---

## 4. Condiciones de Frontera - Aletas Semicirculares

### Centro de la Aleta (r=0)
Condición de simetría radial:

$$\left. \frac{\partial T}{\partial r} \right|_{r=0} = 0$$

**Justificación:** Por simetría geométrica, no hay flujo radial en el centro.

### Superficie Curva (r=R)
Condición de Robin (convección con aire):

$$-k_s \left. \frac{\partial T}{\partial r} \right|_{r=R} = h_{aire} (T_s - T_\infty)$$

**Aplicable en:** $0 \leq \theta \leq \pi$

### Bordes Angulares (θ=0 y θ=π)
Estas son las líneas de contacto con la placa base (diámetro del semicírculo).
Se aplican condiciones de continuidad (ver sección siguiente).

---

## 5. Condiciones de Interfaz - Placa-Aleta

Las aletas están unidas a la placa a lo largo del diámetro del semicírculo.

### Ubicación de las Interfaces
Para cada aleta k (k=1,2,3):
- Centro en $x_k$: x₁=0.005 m, x₂=0.015 m, x₃=0.025 m
- Diámetro: desde $(x_k - R)$ hasta $(x_k + R)$ en la dirección x
- Posición vertical: $y = e_{base}$ (tope de la placa)

### Continuidad de Temperatura

A lo largo del diámetro de contacto:

$$T_{aleta}(r, \theta, t)\Big|_{diámetro} = T_{placa}(x, e_{base}, t)\Big|_{interfaz}$$

**Mapeo de coordenadas:**
- Coordenada cartesiana en la placa: $(x, y=e_{base})$
- Coordenada cilíndrica en la aleta: $(r, \theta=0 \text{ o } \pi)$

**Relación:**
$$x = x_k + r \cos(\theta), \quad y = e_{base}$$

### Continuidad de Flujo de Calor

El flujo de calor normal debe ser continuo a través de la interfaz:

$$-k_s \left. \frac{\partial T}{\partial n} \right|_{aleta} = -k_s \left. \frac{\partial T}{\partial n} \right|_{placa}$$

**Donde:**
- $\vec{n}$: Vector normal unitario saliente de cada medio en la interfaz
- Para la placa: $\vec{n} = +\hat{y}$ (apunta hacia arriba)
- Para la aleta: $\vec{n} = -\hat{r}$ cuando $\theta=0$ o $\pi$ (apunta hacia abajo en el diámetro)

**En forma discreta:**

$$k_s \left. \frac{\partial T}{\partial y} \right|_{placa, y=e_{base}} = k_s \left. \frac{\partial T}{\partial r} \right|_{aleta, \theta=0/\pi}$$

**Nota:** Si ambos medios son del mismo material, $k_s$ se cancela, pero la condición de continuidad del gradiente se mantiene.

---

## 6. Implementación Numérica de Interfaces

### Interpolación Cartesiana-Polar
La interfaz placa-aleta requiere interpolación porque:
- La placa usa malla cartesiana (x,y)
- Las aletas usan malla cilíndrica (r,θ)

**Estrategia:**
1. Para cada nodo en $\theta=0$ y $\theta=\pi$ de la aleta, calcular su posición cartesiana $(x,y)$
2. Interpolar linealmente/bilinealmente desde la malla cartesiana de la placa
3. Aplicar las condiciones de continuidad

### Acoplamiento Fluido-Sólido
El término $T_s$ en la ecuación del fluido requiere:
1. Extracción de $T(x, y=0, t)$ de la malla de la placa
2. Interpolación a las posiciones $x_i$ de la malla del fluido
3. Actualización en cada paso de tiempo

---

## Resumen de Condiciones de Frontera

| Superficie | Tipo | Ecuación | Parámetros |
|------------|------|----------|------------|
| Entrada fluido (x=0) | Dirichlet | $T_f = 80°C$ | - |
| Salida fluido (x=Lx) | Neumann | $\partial T_f/\partial x = 0$ | - |
| Agua-Placa (y=0) | Robin | $-k \partial T/\partial y = h(T_s - T_f)$ | $h_{agua}=600$ |
| Placa-Aire (y=e_base) | Robin | $-k \partial T/\partial y = h(T_s - T_\infty)$ | $h_{aire}=10$ |
| Aleta-Aire (r=R) | Robin | $-k \partial T/\partial r = h(T_s - T_\infty)$ | $h_{aire}=10$ |
| Centro aleta (r=0) | Neumann | $\partial T/\partial r = 0$ | - |
| Placa-Aleta (interfaz) | Continuidad | $T_{placa} = T_{aleta}$, flujos iguales | - |

---

## Notas Críticas para Implementación

1. **Condiciones de Robin**: Requieren nodos fantasma o discretización especial (ver archivo de discretización).

2. **Acoplamiento fluido-sólido**: Es bidireccional y requiere iteración o método implícito para estabilidad.

3. **Interpolación de interfaz**: Errores en la interpolación afectan la conservación de energía.

4. **Condición de salida del fluido**: La condición $\partial T_f/\partial x = 0$ es adecuada para flujos desarrollados.

5. **Verificación**: El balance energético global debe cumplirse:
   $$\dot{Q}_{in} = \dot{Q}_{convección} + \frac{dE_{almacenada}}{dt}$$
