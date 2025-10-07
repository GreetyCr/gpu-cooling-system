#!/usr/bin/env python3
"""
CÓDIGO RESUMEN PARA PRESENTACIÓN EN CLASE
==========================================

Sistema de Enfriamiento GPU: Ecuaciones Discretizadas Clave

Este archivo contiene las partes más importantes del código implementado,
mostrando las ecuaciones diferenciales discretizadas y su implementación.

Autor: Sistema de Simulación Térmica
Fecha: Octubre 2025
"""

import numpy as np

# ============================================================================
# 1. ECUACIÓN DE CONDUCCIÓN 2D - PLACA (FTCS)
# ============================================================================

def ecuacion_placa_interna():
    """
    Ecuación de calor 2D en la placa (FTCS - Forward Time Central Space)
    
    ∂T/∂t = α(∂²T/∂x² + ∂²T/∂y²)
    
    Discretización:
    T[i,j]^(n+1) = T[i,j]^n + Fo_x * (T[i+1,j]^n - 2T[i,j]^n + T[i-1,j]^n)
                             + Fo_y * (T[i,j+1]^n - 2T[i,j]^n + T[i,j-1]^n)
    
    Donde:
        Fo_x = α * Δt / Δx²  (Número de Fourier en x)
        Fo_y = α * Δt / Δy²  (Número de Fourier en y)
    
    Criterio de estabilidad: Fo_x + Fo_y ≤ 0.5
    """
    # Código real de src/placa.py (líneas 130-140)
    
    # Nodos internos de la placa
    for i in range(1, Nx - 1):
        for j in range(1, Ny - 1):
            T_placa_new[i, j] = (
                T_placa_old[i, j]
                + Fo_x * (
                    T_placa_old[i + 1, j]
                    - 2 * T_placa_old[i, j]
                    + T_placa_old[i - 1, j]
                )
                + Fo_y * (
                    T_placa_old[i, j + 1]
                    - 2 * T_placa_old[i, j]
                    + T_placa_old[i, j - 1]
                )
            )


# ============================================================================
# 2. CONDICIÓN DE FRONTERA ROBIN - CONVECCIÓN
# ============================================================================

def ecuacion_robin_conveccion():
    """
    Condición de frontera Robin: -k ∂T/∂n = h(T_s - T_∞)
    
    En la superficie expuesta al aire (y = e_base):
    
    Discretización con diferencias centrales:
    T[i,Ny-1]^(n+1) = T[i,Ny-1]^n + Fo_y * (T[i,Ny-2]^n - 2T[i,Ny-1]^n + T_ghost^n)
    
    Donde T_ghost se obtiene de la BC Robin:
    T_ghost = T[i,Ny-1] - (2Δy * h/k) * (T[i,Ny-1] - T_inf)
    
    Reordenando:
    T[i,Ny-1]^(n+1) = T[i,Ny-1]^n 
                     + 2*Fo_y * (T[i,Ny-2]^n - T[i,Ny-1]^n)
                     - 2*Fo_y * (h*Δy/k) * (T[i,Ny-1]^n - T_inf)
    """
    # Código real de src/placa.py (líneas 145-165)
    
    coef_aire = (params.h_aire * params.dy) / params.k_s
    
    for i in range(1, Nx - 1):
        # Superficie superior expuesta al aire (y = e_base)
        T_placa_new[i, Ny - 1] = (
            T_placa_old[i, Ny - 1]
            + 2 * Fo_y * (T_placa_old[i, Ny - 2] - T_placa_old[i, Ny - 1])
            - 2 * Fo_y * coef_aire * (T_placa_old[i, Ny - 1] - params.T_inf)
        )


# ============================================================================
# 3. ECUACIÓN DE ADVECCIÓN-DIFUSIÓN 1D - FLUIDO (UPWIND)
# ============================================================================

def ecuacion_fluido_upwind():
    """
    Ecuación de advección-difusión 1D en el fluido:
    
    ∂T/∂t + u ∂T/∂x = α ∂²T/∂x²
    
    Discretización Upwind (u > 0) + Euler explícito:
    T[i]^(n+1) = T[i]^n 
                - CFL * (T[i]^n - T[i-1]^n)
                + Fo * (T[i+1]^n - 2T[i]^n + T[i-1]^n)
    
    Donde:
        CFL = u * Δt / Δx  (Número de Courant)
        Fo = α * Δt / Δx²  (Número de Fourier)
    
    Criterios de estabilidad:
        CFL ≤ 1
        Fo ≤ 0.5
    """
    # Código real de src/fluido.py (líneas 115-130)
    
    for i in range(1, Nf - 1):
        # Advección (upwind hacia i-1 porque u > 0)
        adv = -CFL * (T_fluido_old[i] - T_fluido_old[i - 1])
        
        # Difusión (FTCS)
        dif = Fo * (
            T_fluido_old[i + 1] 
            - 2 * T_fluido_old[i] 
            + T_fluido_old[i - 1]
        )
        
        # Actualización
        T_fluido_new[i] = T_fluido_old[i] + adv + dif


# ============================================================================
# 4. ECUACIÓN EN COORDENADAS CILÍNDRICAS - ALETAS
# ============================================================================

def ecuacion_aletas_cilindricas():
    """
    Ecuación de calor 2D en coordenadas cilíndricas (r, θ):
    
    ∂T/∂t = α [∂²T/∂r² + (1/r)∂T/∂r + (1/r²)∂²T/∂θ²]
    
    Discretización (nodos internos r > 0):
    T[i,j]^(n+1) = T[i,j]^n 
                  + Fo_r * [(T[i+1,j]^n - 2T[i,j]^n + T[i-1,j]^n)
                           + (1/(2i)) * (T[i+1,j]^n - T[i-1,j]^n)]
                  + (Fo_θ / i²) * (T[i,j+1]^n - 2T[i,j]^n + T[i,j-1]^n)
    
    Donde:
        Fo_r = α * Δt / Δr²
        Fo_θ = α * Δt / Δθ²
        i es el índice radial (i=0 en centro, i=Nr-1 en superficie)
    
    Estabilidad más restrictiva: en r_min = Δr
        Fo_r + Fo_θ/r_min² ≤ 0.5
    """
    # Código real de src/aletas.py (líneas 215-240)
    
    for i in range(1, Nr - 1):  # r > 0 (excluye centro)
        r_i = malla_aleta['r'][i, 0]
        
        for j in range(1, Ntheta - 1):
            # Término difusivo radial (segunda derivada)
            d2T_dr2 = (
                T_aleta_old[i + 1, j] 
                - 2 * T_aleta_old[i, j] 
                + T_aleta_old[i - 1, j]
            ) / dr2
            
            # Término de primera derivada radial (1/r)
            dT_dr = (T_aleta_old[i + 1, j] - T_aleta_old[i - 1, j]) / (2 * dr)
            term_radial = d2T_dr2 + (1 / r_i) * dT_dr
            
            # Término difusivo angular (1/r²)
            d2T_dtheta2 = (
                T_aleta_old[i, j + 1] 
                - 2 * T_aleta_old[i, j] 
                + T_aleta_old[i, j - 1]
            ) / dtheta2
            term_angular = (1 / r_i**2) * d2T_dtheta2
            
            # Actualización temporal
            T_aleta_new[i, j] = (
                T_aleta_old[i, j] 
                + alpha * dt * (term_radial + term_angular)
            )


# ============================================================================
# 5. TRATAMIENTO DE SINGULARIDAD EN r=0 (REGLA DE L'HÔPITAL)
# ============================================================================

def ecuacion_centro_aleta():
    """
    En el centro de la aleta (r = 0), la ecuación tiene una singularidad.
    
    Aplicando regla de L'Hôpital y simetría:
    
    lim(r→0) [(1/r)∂T/∂r] = ∂²T/∂r²
    
    Por lo tanto en r=0:
    ∂T/∂t = α [2∂²T/∂r² + (1/r²)∂²T/∂θ²]
    
    Como r→0, el término angular domina:
    ∂T/∂t ≈ 2α ∂²T/∂r²
    
    Discretización:
    T[0,j]^(n+1) = T[0,j]^n + 2*Fo_r * Σ_k [T[1,k]^n - T[0,j]^n] / Nθ
    
    Donde Σ_k es la suma sobre todos los ángulos k=0...Nθ-1
    (Promedio de vecinos en primera capa radial)
    """
    # Código real de src/aletas.py (líneas 180-200)
    
    # Centro de la aleta (r=0)
    i = 0
    for j in range(Ntheta):
        # Promedio de vecinos en primera capa radial
        vecinos_suma = np.sum(T_aleta_old[1, :])
        promedio_vecinos = vecinos_suma / Ntheta
        
        # Actualización (2 * Fo_r por L'Hôpital)
        T_aleta_new[i, j] = (
            T_aleta_old[i, j] 
            + 2 * Fo_r * (promedio_vecinos - T_aleta_old[i, j])
        )


# ============================================================================
# 6. ACOPLAMIENTO TÉRMICO - INTERPOLACIÓN BILINEAL
# ============================================================================

def interpolacion_bilinear_2d():
    """
    Acoplamiento térmico entre placa (malla Cartesiana) y aletas (malla cilíndrica)
    
    Para cada punto de la base de la aleta en (r, θ):
    1. Convertir a coordenadas Cartesianas: x = x_centro + r*cos(θ), y = 0
    2. Encontrar celda [x_i, x_i+1] × [y_j, y_j+1] que contiene (x, y)
    3. Interpolación bilineal:
       
       T(x,y) = (1-wx)*(1-wy)*T[i,j]   + wx*(1-wy)*T[i+1,j]
              + (1-wx)*wy*T[i,j+1]     + wx*wy*T[i+1,j+1]
       
       Donde:
           wx = (x - x_i) / Δx
           wy = (y - y_j) / Δy
    
    Implementación con scipy.interpolate.RegularGridInterpolator
    """
    # Código real de src/acoplamiento.py (líneas 160-200)
    
    from scipy.interpolate import RegularGridInterpolator
    
    # Crear interpolador 2D
    x_placa = mallas['placa']['x'][0, :]  # Coordenadas x únicas
    y_placa = mallas['placa']['y'][:, 0]  # Coordenadas y únicas
    
    interpolador = RegularGridInterpolator(
        (x_placa, y_placa),
        T_placa.T,  # Transponer para match (x, y) shape
        method='linear',
        bounds_error=False,
        fill_value=None
    )
    
    # Para cada nodo de la base de la aleta
    for i_aleta in range(Nr_aleta):
        for j_aleta in [0, Ntheta_aleta - 1]:  # θ=0 y θ=π
            # Coordenadas cilíndricas
            r = mallas['aletas'][k]['r'][i_aleta, j_aleta]
            theta = mallas['aletas'][k]['theta'][i_aleta, j_aleta]
            
            # Convertir a Cartesianas
            x_objetivo = x_centro_aleta + r * np.cos(theta)
            y_objetivo = 0.0  # Base de la aleta
            
            # Interpolar temperatura
            T_interpolada = interpolador([x_objetivo, y_objetivo])[0]
            
            # Aplicar como condición Dirichlet
            T_aletas[k][i_aleta, j_aleta] = T_interpolada


# ============================================================================
# 7. CRITERIOS DE ESTABILIDAD
# ============================================================================

def criterios_estabilidad():
    """
    Criterios de estabilidad para esquemas explícitos:
    
    1. FLUIDO (1D):
       - CFL = u*Δt/Δx ≤ 1       (Courant para advección)
       - Fo = α*Δt/Δx² ≤ 0.5     (Fourier para difusión)
    
    2. PLACA (2D Cartesiana):
       - Fo_x + Fo_y ≤ 0.5
       - Fo_x = α*Δt/Δx², Fo_y = α*Δt/Δy²
    
    3. ALETAS (2D Cilíndrica):
       - Más restrictivo en r_min = Δr:
         Fo_r + Fo_θ/r_min² ≤ 0.5
       - Para r=5mm, Δr=0.5mm: r_min² = 2.5×10⁻⁷
       - Fo_θ/r_min² puede ser muy grande → dt muy pequeño
    
    Ejemplo de cálculo de dt para aletas:
    """
    # Código real de src/solucionador.py (líneas 55-80)
    
    # Geometría
    r = 0.005  # 5 mm
    Nr_aleta = 20
    Ntheta_aleta = 10
    
    dr = r / (Nr_aleta - 1)
    dtheta = np.pi / (Ntheta_aleta - 1)
    
    # r_min es el primer nodo después del centro
    r_min = dr
    
    # Difusividad térmica (aluminio)
    alpha = 8.418e-05  # m²/s
    
    # Número de Fourier radial y angular
    Fo_r_max = alpha / dr**2
    Fo_theta_max = alpha / (r_min * dtheta)**2
    
    # Suma debe ser < 0.5
    Fo_total = Fo_r_max + Fo_theta_max
    
    # Calcular dt máximo
    dt_max = 0.5 / Fo_total  # ≈ 3.06×10⁻⁵ s
    
    # Usar 80% del máximo por seguridad
    dt_aletas = 0.8 * dt_max
    
    print(f"dt_max para aletas: {dt_max:.2e} s")
    print(f"dt usado: {dt_aletas:.2e} s")
    print(f"Comparación con placa: dt_placa/dt_aletas = {dt_placa/dt_aletas:.1f}x")


# ============================================================================
# 8. CONVERGENCIA Y ESTADO ESTACIONARIO
# ============================================================================

def criterio_convergencia():
    """
    Criterio para detectar estado estacionario:
    
    max|dT/dt| < ε
    
    Donde ε es la tolerancia (típicamente 1×10⁻³ K/s)
    
    Implementación:
    """
    # Código real de src/solucionador.py (líneas 120-145)
    
    def verificar_convergencia(T_old, T_new, dt, epsilon):
        """
        Verifica si el sistema alcanzó estado estacionario.
        
        Returns:
            bool: True si convergió, False en caso contrario
        """
        # Calcular dT/dt para cada dominio
        dT_dt_fluido = np.abs((T_new['fluido'] - T_old['fluido']) / dt)
        dT_dt_placa = np.abs((T_new['placa'] - T_old['placa']) / dt)
        dT_dt_aletas = [
            np.abs((T_new['aletas'][k] - T_old['aletas'][k]) / dt)
            for k in range(3)
        ]
        
        # Máximo cambio en todo el sistema
        max_dT_dt = max(
            dT_dt_fluido.max(),
            dT_dt_placa.max(),
            max([dT.max() for dT in dT_dt_aletas])
        )
        
        return max_dT_dt < epsilon


# ============================================================================
# 9. NÚMEROS ADIMENSIONALES RELEVANTES
# ============================================================================

def numeros_adimensionales():
    """
    Números adimensionales clave en el problema:
    
    1. NÚMERO DE BIOT (Bi):
       Bi = h*L/k
       - Relación entre resistencia convectiva y conductiva
       - Bi << 1: Temperatura uniforme en sólido (resistencia externa domina)
       - Bi >> 1: Gradientes importantes en sólido (resistencia interna domina)
    
    2. NÚMERO DE FOURIER (Fo):
       Fo = α*t/L²
       - Tiempo adimensional
       - Fo ≈ 1: Tiempo característico de difusión
    
    3. NÚMERO DE PÉCLET (Pe):
       Pe = u*L/α
       - Relación entre advección y difusión
       - Pe >> 1: Advección domina (convección forzada)
       - Pe << 1: Difusión domina
    
    4. NÚMERO DE REYNOLDS (Re):
       Re = ρ*u*D/μ
       - Naturaleza del flujo (laminar vs turbulento)
       - Re < 2300: Laminar
    
    Cálculo para nuestro sistema:
    """
    # Parámetros del sistema
    h_agua = 5000  # W/(m²·K) - coeficiente convectivo agua
    h_aire = 10    # W/(m²·K) - coeficiente convectivo aire
    k_Al = 237     # W/(m·K) - conductividad aluminio
    k_SS = 16      # W/(m·K) - conductividad acero inoxidable
    L_placa = 0.01 # m - espesor placa
    r_aleta = 0.005 # m - radio aleta
    u = 1.0        # m/s - velocidad fluido
    alpha_Al = 8.418e-05  # m²/s
    alpha_SS = 4.074e-06  # m²/s
    
    # Número de Biot
    Bi_placa_agua_Al = (h_agua * L_placa) / k_Al
    Bi_placa_aire_Al = (h_aire * L_placa) / k_Al
    Bi_aleta_Al = (h_aire * r_aleta) / k_Al
    
    Bi_placa_agua_SS = (h_agua * L_placa) / k_SS
    Bi_placa_aire_SS = (h_aire * L_placa) / k_SS
    Bi_aleta_SS = (h_aire * r_aleta) / k_SS
    
    print("NÚMERO DE BIOT:")
    print(f"  Placa-Agua (Al): {Bi_placa_agua_Al:.3f}")
    print(f"  Placa-Aire (Al): {Bi_placa_aire_Al:.6f}")
    print(f"  Aleta (Al): {Bi_aleta_Al:.6f}")
    print(f"  Placa-Agua (SS): {Bi_placa_agua_SS:.3f}")
    print(f"  Placa-Aire (SS): {Bi_placa_aire_SS:.4f}")
    print(f"  Aleta (SS): {Bi_aleta_SS:.5f}")
    
    # Interpretación:
    # Bi_placa_agua > 0.1 → Gradientes importantes en placa con agua
    # Bi_aire << 1 → Temperatura casi uniforme expuesta al aire
    
    # Número de Fourier (para t=60s)
    t = 60  # s
    Fo_placa_Al = (alpha_Al * t) / L_placa**2
    Fo_placa_SS = (alpha_SS * t) / L_placa**2
    Fo_aleta_Al = (alpha_Al * t) / r_aleta**2
    Fo_aleta_SS = (alpha_SS * t) / r_aleta**2
    
    print(f"\nNÚMERO DE FOURIER (t=60s):")
    print(f"  Placa (Al): {Fo_placa_Al:.1f}")
    print(f"  Placa (SS): {Fo_placa_SS:.1f}")
    print(f"  Aleta (Al): {Fo_aleta_Al:.1f}")
    print(f"  Aleta (SS): {Fo_aleta_SS:.2f}")
    
    # Interpretación:
    # Fo > 1 → Sistema ha tenido tiempo suficiente para difundir
    # Fo_Al >> Fo_SS → Aluminio responde mucho más rápido


# ============================================================================
# EJECUCIÓN DE EJEMPLO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CÓDIGO RESUMEN - SISTEMA DE ENFRIAMIENTO GPU")
    print("=" * 70)
    print("\nEste archivo muestra las ecuaciones discretizadas clave.")
    print("Ver docstrings de cada función para detalles matemáticos.\n")
    
    # Ejemplo: Números adimensionales
    numeros_adimensionales()
    
    print("\n" + "=" * 70)
    print("Para código completo, ver módulos en src/:")
    print("  - src/fluido.py: Ecuación advección-difusión 1D")
    print("  - src/placa.py: Ecuación de calor 2D Cartesiana")
    print("  - src/aletas.py: Ecuación de calor 2D cilíndrica")
    print("  - src/acoplamiento.py: Interpolación y acoplamiento")
    print("  - src/solucionador.py: Bucle temporal y convergencia")
    print("=" * 70)
