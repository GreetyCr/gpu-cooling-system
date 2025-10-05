# INSTRUCCIONES: IMPLEMENTACIÓN ECUACIONES SECCIÓN 2.5

## Objetivo de este Documento

Este archivo contiene instrucciones paso a paso para implementar las **ecuaciones discretizadas** de la sección 2.5 del documento del proyecto. Estas son las ecuaciones DESPEJADAS que se usarán en el código Python.

**IMPORTANTE:** Estas instrucciones deben seguirse DESPUÉS de haber completado:
- ✅ `src/parametros.py` (Clase Parametros)
- ✅ `src/mallas.py` (Generación de mallas)

---

## Ecuaciones a Implementar (de la Sección 2.5)

### 1. Fluido - Upwind + Euler Explícito (Ecuación 11)

$$T_{f,i}^{n+1} = T_{f,i}^n - CFL(T_{f,i}^n - T_{f,i-1}^n) - \gamma\Delta t(T_{f,i}^n - T_{s,i}^n)$$

**Donde:**
- $CFL = \frac{u\Delta t}{\Delta x}$ (para $u > 0$, upwind hacia i-1)
- $\gamma = \frac{h_{agua}}{\rho_{agua} c_{p,agua} e_{agua}} = 4.88 \times 10^{-2}$ s⁻¹
- $T_{s,i}^n$ = Temperatura de la superficie de la placa en $(x_i, y=0)$

**Referencia:** Shu & LeVeque (1991)

---

### 2. Placa - FTCS Explícito (Ecuación 11 del doc)

$$T_{i,j}^{n+1} = T_{i,j}^n + Fo_x(T_{i+1,j}^n - 2T_{i,j}^n + T_{i-1,j}^n) + Fo_y(T_{i,j+1}^n - 2T_{i,j}^n + T_{i,j-1}^n)$$

**Donde:**
- $Fo_x = \frac{\alpha \Delta t}{\Delta x^2}$
- $Fo_y = \frac{\alpha \Delta t}{\Delta y^2}$

**Referencia:** Hensen & Nakhi (1994)

---

### 3. Condiciones Robin Discretas (Ecuaciones 12, 13, 14)

#### 3a. Placa - Cara agua (j=0) con nodo fantasma (Ecuación 12):

$$T_{i,-1} = T_{i,0} - \frac{h_{agua}\Delta y}{k}(T_{i,0} - T_{f,i})$$

#### 3b. Placa - Cámara aire (j=Ny) (Ecuación 13):

$$T_{i,Ny+1} = T_{i,Ny} - \frac{h_{aire}\Delta y}{k}(T_{i,Ny} - T_\infty)$$

#### 3c. Aleta - Superficie curva (r=R) (Ecuación 14):

$$T_{R+1,k} = T_{R,k} - \frac{h_{aire}\Delta r}{k}(T_{R,k} - T_\infty)$$

---

### 4. Aletas - FTCS Cilíndrico con Simetría en r=0

#### 4a. Para r > 0 (Ecuación 15):

$$T_{j,k}^{n+1} = T_{j,k}^n + Fo_r\left(T_{j+1,k}^n - 2T_{j,k}^n + T_{j-1,k}^n + \frac{\Delta r}{r_j}(T_{j+1,k}^n - T_{j-1,k}^n)\right) + Fo_\theta \frac{1}{r_j^2}(T_{j,k+1}^n - 2T_{j,k}^n + T_{j,k-1}^n)$$

**Donde:**
- $Fo_r = \frac{\alpha \Delta t}{\Delta r^2}$
- $Fo_\theta = \frac{\alpha \Delta t}{(r\Delta\theta)^2}$

**Referencia:** Hensen & Nakhi (1994)

#### 4b. Para r = 0 usando L'Hôpital (Ecuación 16):

$$T_{0,k}^{n+1} = T_{0,k}^n + 2Fo_r(T_{1,k}^n - T_{0,k}^n)$$

---

## PLAN DE IMPLEMENTACIÓN

### FASE 1: Implementar Solver del Fluido

**Archivo a crear:** `src/fluido.py`

#### Tarea 1.1: Función de Inicialización
```python
def inicializar_fluido(params, mallas):
    """
    Inicializa el campo de temperatura del fluido
    
    Args:
        params: Objeto Parametros
        mallas: Diccionario con las mallas
    
    Returns:
        T_fluido: Array 1D con temperatura inicial
    """
```

**Instrucciones para Cursor:**
1. Lee `contexto/02_parametros_sistema.md` para obtener valores de temperatura inicial
2. Crea array 1D de tamaño `Nx_fluido`
3. Inicializa todo a `T_inicial` (23°C = 296.15 K)
4. Aplica condición de entrada: `T_fluido[0] = T_f_in` (80°C = 353.15 K)
5. Incluye docstring completo
6. Incluye validaciones (no NaN, no Inf, rango físico)

#### Tarea 1.2: Función de Actualización (ECUACIÓN 11)
```python
def actualizar_fluido(T_fluido_old, T_superficie_placa, params, mallas, dt):
    """
    Actualiza temperatura del fluido usando Upwind + Euler Explícito
    Implementa la Ecuación 11 del documento
    
    Args:
        T_fluido_old: Array 1D temperatura actual del fluido
        T_superficie_placa: Array 1D temperatura superficie placa (y=0)
        params: Objeto Parametros
        mallas: Diccionario con las mallas
        dt: Paso de tiempo
    
    Returns:
        T_fluido_new: Array 1D temperatura actualizada
    """
```

**Instrucciones detalladas para Cursor:**

1. **Extraer parámetros necesarios:**
   - `u = params.u` (velocidad)
   - `gamma = params.gamma` (parámetro de acople)
   - `dx = mallas['fluido']['dx']`
   - `Nx = params.Nx_fluido`

2. **Calcular CFL:**
   ```python
   CFL = u * dt / dx
   ```

3. **Validar estabilidad ANTES de continuar:**
   ```python
   assert CFL < 1.0, f"INESTABLE: CFL = {CFL:.3f} > 1"
   ```

4. **Interpolar T_superficie si las mallas no coinciden:**
   - Si `len(T_superficie_placa) != Nx`: usar interpolación lineal
   - Si coinciden: usar directamente

5. **Implementar ECUACIÓN 11:**
   - Para nodos internos (i = 1 hasta Nx-2):
     ```python
     T_new[i] = T_old[i] - CFL*(T_old[i] - T_old[i-1]) - gamma*dt*(T_old[i] - T_s[i])
     ```

6. **Condiciones de frontera:**
   - Entrada (i=0): `T_new[0] = params.T_f_in` (Dirichlet)
   - Salida (i=Nx-1): `T_new[Nx-1] = T_new[Nx-2]` (Neumann, derivada=0)

7. **Validar salida:**
   ```python
   assert not np.isnan(T_new).any(), "Output tiene NaN"
   assert not np.isinf(T_new).any(), "Output tiene Inf"
   assert T_new.min() > 200, "Temperatura < 200K (no físico)"
   assert T_new.max() < 400, "Temperatura > 400K (no físico)"
   ```

8. **Retornar resultado**

**IMPORTANTE:**
- Usar vectorización NumPy para nodos internos
- NO usar bucles for si es posible
- Consultar `contexto/05_discretizacion_numerica.md` sección 4.1 para más detalles

---

### FASE 2: Implementar Solver de la Placa

**Archivo a crear:** `src/placa.py`

#### Tarea 2.1: Función de Inicialización
```python
def inicializar_placa(params, mallas):
    """
    Inicializa el campo de temperatura de la placa
    
    Returns:
        T_placa: Array 2D (Ny, Nx) con temperatura inicial
    """
```

**Instrucciones:**
1. Crear array 2D de tamaño `(Ny_placa, Nx_placa)`
2. Inicializar todo a `T_inicial` (296.15 K)
3. Validaciones estándar

#### Tarea 2.2: Función para Nodos Internos (ECUACIÓN 11 placa)
```python
def actualizar_placa_internos(T_old, Fo_x, Fo_y, Nx, Ny):
    """
    Actualiza nodos internos de la placa usando FTCS
    Implementa la Ecuación 11 (placa) del documento
    
    Args:
        T_old: Array 2D (Ny, Nx) temperatura actual
        Fo_x: Número de Fourier en x
        Fo_y: Número de Fourier en y
        Nx, Ny: Dimensiones de la malla
    
    Returns:
        T_new: Array 2D temperatura actualizada (solo internos)
    """
```

**Instrucciones detalladas:**

1. **Validar estabilidad ANTES:**
   ```python
   Fo_total = Fo_x + Fo_y
   assert Fo_total < 0.5, f"INESTABLE: Fourier = {Fo_total:.3f} > 0.5"
   ```

2. **Implementar ECUACIÓN 11 (vectorizada):**
   ```python
   T_new[1:-1, 1:-1] = (T_old[1:-1, 1:-1] 
                        + Fo_x * (T_old[1:-1, 2:] - 2*T_old[1:-1, 1:-1] + T_old[1:-1, :-2])
                        + Fo_y * (T_old[2:, 1:-1] - 2*T_old[1:-1, 1:-1] + T_old[:-2, 1:-1]))
   ```

3. **Validar salida**

#### Tarea 2.3: Función para Condición Robin en Agua (ECUACIÓN 12)
```python
def aplicar_bc_agua(T_placa, T_fluido, params, mallas):
    """
    Aplica condición Robin en interfaz agua-placa (j=0)
    Implementa la Ecuación 12 del documento
    
    Args:
        T_placa: Array 2D temperatura de la placa
        T_fluido: Array 1D temperatura del fluido
        params: Objeto Parametros
        mallas: Diccionario con mallas
    
    Returns:
        T_placa: Modificado con BC aplicado en j=0
    """
```

**Instrucciones detalladas:**

1. **Calcular coeficiente:**
   ```python
   coef = h_agua * dy / k
   ```

2. **Para cada i (excepto bordes):**
   - Calcular nodo fantasma usando ECUACIÓN 12:
     ```python
     T_fantasma[i] = T_placa[0, i] - coef * (T_placa[0, i] - T_fluido[i])
     ```

3. **Aplicar en ecuación FTCS:**
   - Reemplazar `T_placa[-1, i]` por `T_fantasma[i]` en el cálculo

4. **Actualizar `T_placa[0, i]`** usando FTCS con el nodo fantasma

**Ver `contexto/05_discretizacion_numerica.md` sección 4.3 para detalles**

#### Tarea 2.4: Función para Condición Robin en Aire (ECUACIÓN 13)
```python
def aplicar_bc_aire(T_placa, params, mallas):
    """
    Aplica condición Robin en superficie superior (j=Ny)
    Implementa la Ecuación 13 del documento
    """
```

**Similar a 2.3 pero usando:**
- `h_aire` en lugar de `h_agua`
- `T_inf` en lugar de `T_fluido`
- En `j = Ny` (última fila)

#### Tarea 2.5: Función Maestra de Actualización
```python
def actualizar_placa(T_placa_old, T_fluido, params, mallas, dt):
    """
    Actualiza toda la placa: internos + fronteras
    
    Returns:
        T_placa_new: Array 2D actualizado
    """
```

**Instrucciones:**
1. Calcular `Fo_x` y `Fo_y`
2. Validar estabilidad
3. Actualizar nodos internos (llamar a 2.2)
4. Aplicar BC agua (llamar a 2.3)
5. Aplicar BC aire (llamar a 2.4)
6. Aplicar BC laterales (simetría o valor fijo)
7. Validar salida
8. Retornar

---

### FASE 3: Implementar Solver de Aletas

**Archivo a crear:** `src/aletas.py`

#### Tarea 3.1: Función de Inicialización
```python
def inicializar_aleta(params, mallas, k_aleta):
    """
    Inicializa una aleta
    
    Args:
        k_aleta: Índice de la aleta (0, 1, o 2)
    
    Returns:
        T_aleta: Array 2D (Ntheta, Nr) temperatura inicial
    """
```

#### Tarea 3.2: Función para r > 0 (ECUACIÓN 15)
```python
def actualizar_aleta_interior(T_old, params, mallas, k_aleta, dt):
    """
    Actualiza nodos con r > 0 usando FTCS cilíndrico
    Implementa la Ecuación 15 del documento
    """
```

**Instrucciones detalladas:**

1. **Extraer parámetros:**
   ```python
   dr = mallas['aletas'][k_aleta]['dr']
   dtheta = mallas['aletas'][k_aleta]['dtheta']
   Nr = params.Nr_aleta
   Ntheta = params.Ntheta_aleta
   alpha = params.alpha
   ```

2. **Calcular números de Fourier:**
   ```python
   Fo_r = alpha * dt / dr**2
   Fo_theta = alpha * dt / (r * dtheta)**2  # Nota: r varía
   ```

3. **IMPORTANTE:** `Fo_theta` depende de `r`, calcular dentro del bucle

4. **Implementar ECUACIÓN 15:**
   - Para j = 1 hasta Nr-2 (r > 0):
     - Calcular `r_j = j * dr`
     - Calcular `Fo_theta_j = alpha * dt / (r_j * dtheta)**2`
     - Para m = 1 hasta Ntheta-2:
       ```python
       d2T_dr2 = T_old[m, j+1] - 2*T_old[m, j] + T_old[m, j-1]
       dT_dr = (T_old[m, j+1] - T_old[m, j-1]) / (2*dr)
       d2T_dtheta2 = T_old[m+1, j] - 2*T_old[m, j] + T_old[m-1, j]
       
       T_new[m, j] = (T_old[m, j] 
                      + Fo_r * (d2T_dr2 + dT_dr / r_j)
                      + Fo_theta_j * d2T_dtheta2)
       ```

5. **Validar estabilidad:** Verificar `Fo_r + Fo_theta < 0.5`

#### Tarea 3.3: Función para r = 0 (ECUACIÓN 16)
```python
def actualizar_aleta_centro(T_old, Fo_r, Ntheta):
    """
    Actualiza nodos en r=0 usando L'Hôpital
    Implementa la Ecuación 16 del documento
    """
```

**Instrucciones:**

1. **Implementar ECUACIÓN 16:**
   ```python
   for m in range(Ntheta):
       T_new[m, 0] = T_old[m, 0] + 2*Fo_r*(T_old[m, 1] - T_old[m, 0])
   ```

2. **NOTA:** En el centro, la temperatura no depende de θ por simetría

#### Tarea 3.4: Función para BC en r=R (ECUACIÓN 14)
```python
def aplicar_bc_superficie_aleta(T_aleta, params, mallas, k_aleta, dt):
    """
    Aplica condición Robin en r=R
    Implementa la Ecuación 14 del documento
    """
```

**Similar a las BCs de la placa, usar ECUACIÓN 14**

#### Tarea 3.5: Función Maestra
```python
def actualizar_aleta(T_aleta_old, params, mallas, k_aleta, dt):
    """
    Actualiza una aleta completa
    """
```

**Integrar todas las funciones anteriores**

---

## ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Sesión 1: Fluido
1. ✅ Implementar `fluido.py` completo
2. ✅ Crear `tests/test_fluido.py`
3. ✅ Verificar CFL < 1
4. ✅ Testear con caso simple
5. ✅ Actualizar WORKLOG.md

### Sesión 2: Placa
1. ✅ Implementar `placa.py` - inicialización
2. ✅ Implementar nodos internos (ECUACIÓN 11)
3. ✅ Implementar BC agua (ECUACIÓN 12)
4. ✅ Implementar BC aire (ECUACIÓN 13)
5. ✅ Integrar en función maestra
6. ✅ Crear `tests/test_placa.py`
7. ✅ Verificar Fourier < 0.5
8. ✅ Testear con caso simple
9. ✅ Actualizar WORKLOG.md

### Sesión 3: Aletas
1. ✅ Implementar `aletas.py` - inicialización
2. ✅ Implementar centro r=0 (ECUACIÓN 16)
3. ✅ Implementar interior r>0 (ECUACIÓN 15)
4. ✅ Implementar BC r=R (ECUACIÓN 14)
5. ✅ Integrar en función maestra
6. ✅ Crear `tests/test_aletas.py`
7. ✅ Testear con caso simple
8. ✅ Actualizar WORKLOG.md

---

## CHECKLIST POR ECUACIÓN

### ✅ Ecuación 11 (Fluido)
- [ ] Implementada correctamente
- [ ] CFL < 1 verificado
- [ ] Condiciones de frontera aplicadas
- [ ] Validaciones incluidas
- [ ] Testeada

### ✅ Ecuación 11 (Placa)
- [ ] Implementada correctamente
- [ ] Fourier < 0.5 verificado
- [ ] Vectorizada con NumPy
- [ ] Validaciones incluidas
- [ ] Testeada

### ✅ Ecuación 12 (BC Agua)
- [ ] Implementada correctamente
- [ ] Nodo fantasma calculado bien
- [ ] Integrada con FTCS
- [ ] Testeada

### ✅ Ecuación 13 (BC Aire Placa)
- [ ] Implementada correctamente
- [ ] Nodo fantasma calculado bien
- [ ] Integrada con FTCS
- [ ] Testeada

### ✅ Ecuación 14 (BC Aire Aleta)
- [ ] Implementada correctamente
- [ ] Nodo fantasma calculado bien
- [ ] Integrada con FTCS cilíndrico
- [ ] Testeada

### ✅ Ecuación 15 (Aleta Interior)
- [ ] Implementada correctamente
- [ ] Términos radiales correctos
- [ ] Términos angulares correctos
- [ ] Fourier variable con r
- [ ] Testeada

### ✅ Ecuación 16 (Aleta Centro)
- [ ] Implementada correctamente
- [ ] L'Hôpital aplicado
- [ ] Independencia de θ verificada
- [ ] Testeada

---

## REFERENCIAS DE CONTEXTO

Para cada ecuación, consultar:

- **Parámetros:** `contexto/02_parametros_sistema.md`
- **Teoría:** `contexto/03_ecuaciones_gobernantes.md`
- **BCs:** `contexto/04_condiciones_frontera.md`
- **Discretización:** `contexto/05_discretizacion_numerica.md`

---

## REGLAS IMPORTANTES

1. **UNA ECUACIÓN A LA VEZ**
   - Implementar completamente antes de pasar a la siguiente
   - Testear cada ecuación por separado

2. **VALIDAR SIEMPRE**
   - Estabilidad (CFL, Fourier)
   - Rango físico (200K < T < 400K)
   - No NaN, no Inf

3. **DOCUMENTAR TODO**
   - Docstrings completos
   - Comentarios sobre qué ecuación implementa
   - Actualizar WORKLOG.md

4. **PREGUNTAR ANTES DE IMPLEMENTAR**
   - Si algo no está claro en la ecuación
   - Si hay duda sobre índices
   - Si necesitas más información

---

## TEMPLATE DE RESPUESTA PARA CURSOR

Cuando implementes cada ecuación, responde con:

```markdown
# Implementación: [Nombre Ecuación]

## Ecuación Original (del documento)
[Mostrar ecuación matemática]

## Entendimiento
[Explicar qué hace la ecuación]

## Preguntas de Clarificación
[Si hay dudas]

## Código Propuesto
[Mostrar código completo]

## Testing
[Cómo se va a testear]

## ¿Procedo a guardar en [archivo]?
```

---

**¡Listo! Usar este documento junto con .cursorrules para implementar las ecuaciones paso a paso.**
