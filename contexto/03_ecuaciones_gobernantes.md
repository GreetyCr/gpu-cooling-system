# Ecuaciones Gobernantes

## 1. Fluido (Agua) - Modelo 1D Convectivo Transitorio

### Ecuación de Energía 1D con Convección

$$\frac{\partial T_f}{\partial t} + u \frac{\partial T_f}{\partial x} = -\gamma (T_f - T_s)$$

**Variables:**
- $T_f(x,t)$: Temperatura del fluido [K]
- $T_s(x,t)$: Temperatura de la superficie sólida en la interfaz agua-placa [K]
- $t$: Tiempo [s]
- $x$: Posición en dirección del flujo [m]

**Parámetros:**
- $u = 0.111$ m/s: Velocidad media del fluido
- $\gamma = 4.88 \times 10^{-2}$ s⁻¹: Parámetro de acoplamiento térmico

**Interpretación física:**
- **Término 1** ($\partial T_f / \partial t$): Cambio temporal de temperatura
- **Término 2** ($u \partial T_f / \partial x$): Advección térmica (transporte por flujo)
- **Término 3** ($-\gamma(T_f - T_s)$): Intercambio térmico con la placa

**Dominio:**
- $0 \leq x \leq L_x = 0.03$ m
- Variable independiente adicional: tiempo $t \geq 0$

---

## 2. Placa Base - Modelo 2D Cartesiano

### Ecuación de Conducción de Calor 2D

$$\frac{\partial T}{\partial t} = \alpha \left( \frac{\partial^2 T}{\partial x^2} + \frac{\partial^2 T}{\partial y^2} \right)$$

**Variables:**
- $T(x,y,t)$: Temperatura en el sólido [K]
- $x$: Posición en dirección del flujo [m]
- $y$: Posición vertical (espesor) [m]
- $t$: Tiempo [s]

**Parámetros (dependen del material):**
- Para Aluminio: $\alpha_{Al} = 6.87 \times 10^{-5}$ m²/s
- Para Acero Inoxidable: $\alpha_{SS} = 4.05 \times 10^{-6}$ m²/s

**Difusividad térmica:**
$$\alpha = \frac{k}{\rho c_p}$$

**Dominio:**
- $0 \leq x \leq L_x = 0.03$ m
- $0 \leq y \leq e_{base} = 0.01$ m
- $t \geq 0$

**Interpretación física:**
- La difusividad térmica $\alpha$ controla la velocidad de propagación del calor
- Mayor $\alpha$ → respuesta más rápida a cambios de temperatura
- $\alpha_{Al} \approx 17 \times \alpha_{SS}$ → el aluminio responde mucho más rápido

---

## 3. Aletas Semicirculares - Modelo 2D Cilíndrico

### Ecuación de Conducción en Coordenadas Cilíndricas

$$\frac{\partial T}{\partial t} = \alpha \left( \frac{\partial^2 T}{\partial r^2} + \frac{1}{r} \frac{\partial T}{\partial r} + \frac{1}{r^2} \frac{\partial^2 T}{\partial \theta^2} \right)$$

**Variables:**
- $T(r,\theta,t)$: Temperatura en la aleta [K]
- $r$: Coordenada radial [m]
- $\theta$: Coordenada angular [radianes]
- $t$: Tiempo [s]

**Dominio (para cada aleta k=1,2,3):**
- $0 \leq r \leq R = 0.004$ m (radio del domo)
- $0 \leq \theta \leq \pi$ (semicírculo)
- $t \geq 0$

### Manejo de la Singularidad en r=0

**Condición de simetría en el centro:**
$$\left. \frac{\partial T}{\partial r} \right|_{r=0} = 0$$

**Aplicación de la Regla de L'Hôpital:**

El término singular $\frac{1}{r} \frac{\partial T}{\partial r}$ cuando $r \to 0$ se evalúa como:

$$\lim_{r \to 0} \frac{1}{r} \frac{\partial T}{\partial r} = \left. \frac{\partial^2 T}{\partial r^2} \right|_{r=0}$$

**Por lo tanto, en r=0 la ecuación se simplifica a:**

$$\frac{\partial T}{\partial t} = \alpha \left( 2 \frac{\partial^2 T}{\partial r^2} + \frac{1}{r^2} \frac{\partial^2 T}{\partial \theta^2} \right) \bigg|_{r=0}$$

En la práctica, para esquemas numéricos en $r=0$, se usa una aproximación especial (ver archivo de discretización).

---

## Resumen de Ecuaciones por Dominio

| Dominio | Dimensionalidad | Ecuación | Variables |
|---------|-----------------|----------|-----------|
| Fluido (agua) | 1D + tiempo | Advección-difusión | $T_f(x,t)$ |
| Placa base | 2D + tiempo | Conducción cartesiana | $T(x,y,t)$ |
| Aletas (×3) | 2D + tiempo | Conducción cilíndrica | $T(r,\theta,t)$ |

---

## Notas para Implementación

1. **Acoplamiento fluido-sólido**: El término $T_s$ en la ecuación del fluido proviene de la temperatura de la placa en $y=0$, requiere interpolación espacial.

2. **Tres aletas independientes**: Cada aleta tiene su propio sistema de coordenadas cilíndricas centrado en $x_k$ (k=1,2,3).

3. **Conservación de energía**: El balance energético global debe verificarse:
   $$\dot{Q}_{agua} = \dot{Q}_{convección,agua} - \dot{Q}_{convección,aire}$$

4. **Escala de tiempo característica**: 
   - Para Al: $\tau_{Al} \sim L^2/\alpha_{Al}$
   - Para SS: $\tau_{SS} \sim L^2/\alpha_{SS}$
   - Donde $L$ es una longitud característica (ej: $e_{base}$)

5. **Números adimensionales relevantes**:
   - Número de Fourier: $Fo = \alpha t / L^2$ (evalúa el estado transitorio)
   - Número de Biot: $Bi = hL/k$ (evalúa resistencia convectiva vs. conductiva)
