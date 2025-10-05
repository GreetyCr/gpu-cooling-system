#!/usr/bin/env python3
"""
Solver 2D para aletas semicirculares en coordenadas cilíndricas (r, θ).

Este módulo implementa la solución numérica de la ecuación de conducción de calor
en coordenadas cilíndricas para 3 aletas semicirculares montadas sobre la placa.

Ecuaciones implementadas:
- Ecuación 14: BC Robin en r=R (convección con aire)
- Ecuación 15: Nodos internos r>0 (FTCS cilíndrico)
- Ecuación 16: Centro r=0 (tratamiento L'Hôpital)

Referencias:
- contexto/03_ecuaciones_gobernantes.md: Ecuación diferencial
- contexto/04_condiciones_frontera.md: Condiciones de frontera
- contexto/05_discretizacion_numerica.md: Ecuaciones discretas 14, 15, 16
- todo/instrucciones_ecuaciones.md: FASE 3

Autor: Sistema de Enfriamiento GPU - Proyecto IQ-0331
Fecha: 2025-10-04
"""

import numpy as np
from typing import Dict, Tuple
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parametros import Parametros


def inicializar_aleta(
    params: Parametros,
    mallas: Dict,
    k_aleta: int
) -> np.ndarray:
    """
    Inicializa el campo de temperatura de una aleta semicircular.
    
    La aleta se inicializa en equilibrio térmico con el ambiente (T_inicial = T_∞).
    
    Args:
        params: Instancia de Parametros con configuración del sistema
        mallas: Diccionario con todas las mallas del sistema
        k_aleta: Índice de la aleta (0, 1, o 2)
    
    Returns:
        T_aleta: Array 2D (Ntheta, Nr) con temperaturas iniciales [K]
                 Índices: T_aleta[m, j] donde m=theta, j=radio
    
    Raises:
        ValueError: Si k_aleta no está en [0, 1, 2]
        AssertionError: Si las dimensiones no coinciden con params
    
    Notes:
        - Shape: (Ntheta_aleta, Nr_aleta) = (20, 10)
        - j=0: centro (r=0)
        - j=9: superficie (r=R)
        - m=0: θ=0 (interfaz con placa)
        - m=19: θ=π (interfaz con placa)
        - Temperatura inicial uniforme: T_inicial
    """
    # Validaciones de entrada
    assert k_aleta in [0, 1, 2], f"k_aleta debe ser 0, 1 o 2, recibido: {k_aleta}"
    assert 'aletas' in mallas, "mallas debe contener la clave 'aletas'"
    assert len(mallas['aletas']) == 3, "Debe haber exactamente 3 aletas"
    
    # Extraer dimensiones
    Ntheta = params.Ntheta_aleta  # 20
    Nr = params.Nr_aleta          # 10
    
    # Verificar consistencia con la malla
    malla_aleta = mallas['aletas'][k_aleta]
    assert malla_aleta['theta'].shape == (Ntheta,), \
        f"Malla theta inconsistente: esperado ({Ntheta},), recibido {malla_aleta['theta'].shape}"
    assert malla_aleta['r'].shape == (Nr,), \
        f"Malla r inconsistente: esperado ({Nr},), recibido {malla_aleta['r'].shape}"
    
    # Inicializar en temperatura ambiente
    T_aleta = np.full((Ntheta, Nr), params.T_inicial, dtype=np.float64)
    
    # Validaciones de salida
    assert T_aleta.shape == (Ntheta, Nr), \
        f"Shape incorrecto: esperado ({Ntheta}, {Nr}), obtenido {T_aleta.shape}"
    assert not np.isnan(T_aleta).any(), "Campo inicial contiene NaN"
    assert not np.isinf(T_aleta).any(), "Campo inicial contiene Inf"
    assert np.all(T_aleta == params.T_inicial), "Temperatura no uniforme"
    
    return T_aleta


def _actualizar_centro_aleta(
    T_old: np.ndarray,
    Fo_r: float,
    params: Parametros
) -> np.ndarray:
    """
    Actualiza los nodos en el centro de la aleta (r=0) usando L'Hôpital.
    
    Implementa la Ecuación 16 del documento de discretización:
    
        T_{0,m}^{n+1} = T_{0,m}^n + 2·Fo_r·(T_{1,m}^n - T_{0,m}^n)
    
    En el centro (r=0), el término 1/r se vuelve singular. Aplicando L'Hôpital,
    la ecuación en coordenadas cilíndricas se reduce a esta forma simplificada.
    
    Args:
        T_old: Campo de temperatura en el paso anterior (Ntheta, Nr) [K]
        Fo_r: Número de Fourier en dirección radial = α·Δt/Δr²
        params: Instancia de Parametros
    
    Returns:
        T_centro: Temperaturas actualizadas en j=0 para todos los m (Ntheta,) [K]
    
    Notes:
        - Por simetría, T en r=0 no depende de θ, pero mantenemos
          el array (Ntheta,) para consistencia dimensional
        - Esta función solo actualiza j=0, no modifica otros nodos
    
    References:
        - Ecuación 16 en contexto/05_discretizacion_numerica.md (línea 193-199)
        - Justificación L'Hôpital en contexto/03_ecuaciones_gobernantes.md
    """
    # Validaciones de entrada
    Ntheta = params.Ntheta_aleta
    assert T_old.shape[0] == Ntheta, f"Dimensión theta incorrecta"
    assert T_old.shape[1] >= 2, "Se necesitan al menos 2 nodos radiales (j=0,1)"
    assert 0 < Fo_r < 1.0, f"Fo_r fuera de rango estable: {Fo_r}"
    
    # Extraer temperaturas
    T_centro_old = T_old[:, 0]  # j=0, todos los m
    T_radio_1 = T_old[:, 1]     # j=1, todos los m
    
    # Ecuación 16: Actualización en r=0
    T_centro_new = T_centro_old + 2.0 * Fo_r * (T_radio_1 - T_centro_old)
    
    # Validaciones de salida
    assert T_centro_new.shape == (Ntheta,), f"Shape incorrecto: {T_centro_new.shape}"
    assert not np.isnan(T_centro_new).any(), "Resultado contiene NaN en centro"
    assert not np.isinf(T_centro_new).any(), "Resultado contiene Inf en centro"
    assert np.all((T_centro_new >= 200) & (T_centro_new <= 500)), \
        f"Temperaturas fuera de rango físico en centro: [{T_centro_new.min():.1f}, {T_centro_new.max():.1f}] K"
    
    return T_centro_new


def _actualizar_interior_aleta(
    T_old: np.ndarray,
    params: Parametros,
    mallas: Dict,
    k_aleta: int,
    dt: float
) -> np.ndarray:
    """
    Actualiza nodos internos de la aleta (r>0) usando FTCS cilíndrico.
    
    Implementa la Ecuación 15 del documento de discretización:
    
        T_{j,m}^{n+1} = T_{j,m}^n 
                        + Fo_r·[∂²T/∂r² + (1/r_j)·∂T/∂r]
                        + Fo_θ(r_j)·(1/r_j²)·∂²T/∂θ²
    
    IMPORTANTE: Fo_θ depende de r_j, debe calcularse para cada j.
    
    Args:
        T_old: Campo de temperatura en el paso anterior (Ntheta, Nr) [K]
        params: Instancia de Parametros
        mallas: Diccionario con todas las mallas
        k_aleta: Índice de la aleta (0, 1, o 2)
        dt: Paso de tiempo [s]
    
    Returns:
        T_new: Campo actualizado solo en nodos internos (Ntheta, Nr) [K]
               j=1..Nr-2 (internos radiales)
               m=1..Ntheta-2 (internos angulares)
    
    Notes:
        - Esta función NO actualiza: j=0 (centro), j=Nr-1 (superficie),
          m=0, m=Ntheta-1 (bordes en theta)
        - Fo_r = α·Δt/Δr² (constante)
        - Fo_θ(r) = α·Δt/(r·Δθ)² (variable con r)
        - Derivadas aproximadas por diferencias centradas de segundo orden
    
    References:
        - Ecuación 15 en contexto/05_discretizacion_numerica.md (línea 181-189)
        - Instrucciones detalladas en todo/instrucciones_ecuaciones.md (línea 328-361)
    """
    # Validaciones de entrada
    Ntheta = params.Ntheta_aleta
    Nr = params.Nr_aleta
    alpha = params.alpha_s
    
    assert T_old.shape == (Ntheta, Nr), f"Shape incorrecto: {T_old.shape}"
    assert dt > 0, f"dt debe ser positivo: {dt}"
    assert k_aleta in [0, 1, 2], f"k_aleta inválido: {k_aleta}"
    
    # Extraer parámetros de la malla
    malla_aleta = mallas['aletas'][k_aleta]
    dr = malla_aleta['dr']
    dtheta = malla_aleta['dtheta']
    r_array = malla_aleta['r']  # Array de radios: r[j] = j * dr
    
    # Calcular Fourier radial (constante)
    Fo_r = alpha * dt / (dr**2)
    
    # Crear array de salida (copia)
    T_new = T_old.copy()
    
    # Calcular Fo_theta (constante, sin dependencia espacial)
    # Nota: Fo_θ = α·Δt (NO dividido por (r·Δθ)²)
    # El término espacial 1/r² y 1/Δθ² se aplican explícitamente en la ecuación
    Fo_theta = alpha * dt
    
    # Actualizar nodos internos: j=1..Nr-2, m=1..Ntheta-2
    for j in range(1, Nr - 1):
        r_j = r_array[j]  # Radio en el nodo j
        
        # Validar que no estamos en r=0 (debe manejarse aparte)
        assert r_j > 0, f"r_j debe ser > 0 para nodos internos, pero r[{j}] = {r_j}"
        
        # Actualizar para todos los ángulos internos
        for m in range(1, Ntheta - 1):
            # Diferencias finitas en dirección radial (SIN normalizar por dr²)
            diff_r_2nd = (T_old[m, j+1] - 2.0*T_old[m, j] + T_old[m, j-1])
            diff_r_1st = (T_old[m, j+1] - T_old[m, j-1])
            
            # Diferencia finita en dirección angular (SIN normalizar por dtheta²)
            diff_theta_2nd = (T_old[m+1, j] - 2.0*T_old[m, j] + T_old[m-1, j])
            
            # Ecuación 15 (línea 186 del documento):
            # T_{j,m}^{n+1} = T_{j,m}^n + Fo_r·[ΔΔr + (Δr/r_j)·Δr] + Fo_θ·(1/r_j²)·ΔΔθ
            T_new[m, j] = (T_old[m, j] 
                          + Fo_r * (diff_r_2nd + (dr / r_j) * diff_r_1st)
                          + Fo_theta * (1.0 / (r_j * dtheta)**2) * diff_theta_2nd)
    
    # Validaciones de salida
    assert T_new.shape == T_old.shape, "Shape cambió durante actualización"
    assert not np.isnan(T_new).any(), "Resultado contiene NaN en interior"
    assert not np.isinf(T_new).any(), "Resultado contiene Inf en interior"
    
    # Verificar que solo se actualizaron nodos internos
    assert np.array_equal(T_new[:, 0], T_old[:, 0]), "Se modificó j=0 (centro)"
    assert np.array_equal(T_new[:, -1], T_old[:, -1]), "Se modificó j=Nr-1 (superficie)"
    assert np.array_equal(T_new[0, :], T_old[0, :]), "Se modificó m=0 (borde theta)"
    assert np.array_equal(T_new[-1, :], T_old[-1, :]), "Se modificó m=Ntheta-1 (borde theta)"
    
    return T_new


def _aplicar_bc_superficie_aleta(
    T_new: np.ndarray,
    T_old: np.ndarray,
    params: Parametros,
    mallas: Dict,
    k_aleta: int,
    dt: float
) -> np.ndarray:
    """
    Aplica condición de frontera Robin en la superficie de la aleta (r=R).
    
    Implementa la Ecuación 14 del documento de discretización:
    
        T_{R,m}^{n+1} = T_{R,m}^n 
                        + 2·Fo_r·[(T_{R-1,m}^n - T_{R,m}^n) + β_aire·(T_{R,m}^n - T_∞)]
                        + Fo_θ(R)·(1/R²)·(T_{R,m+1}^n - 2·T_{R,m}^n + T_{R,m-1}^n)
    
    donde β_aire = h_aire·Δr/k_s
    
    Esta BC modela la convección con el aire ambiente en la superficie exterior.
    
    Args:
        T_new: Campo de temperatura actualizado parcialmente (Ntheta, Nr) [K]
        T_old: Campo de temperatura en el paso anterior (Ntheta, Nr) [K]
        params: Instancia de Parametros
        mallas: Diccionario con todas las mallas
        k_aleta: Índice de la aleta (0, 1, o 2)
        dt: Paso de tiempo [s]
    
    Returns:
        T_new: Campo actualizado con BC en r=R (j=Nr-1) para m=1..Ntheta-2 [K]
    
    Notes:
        - Solo actualiza j=Nr-1 (superficie)
        - No actualiza m=0 ni m=Ntheta-1 (se manejan aparte)
        - Usa nodo fantasma implícito para derivada radial
        - Similar a BC Robin de la placa (Ecuación 13)
    
    References:
        - Ecuación 14 en contexto/05_discretizacion_numerica.md (línea 201-209)
        - BC Robin en contexto/04_condiciones_frontera.md
    """
    # Validaciones de entrada
    Ntheta = params.Ntheta_aleta
    Nr = params.Nr_aleta
    alpha = params.alpha_s
    h_aire = params.h_aire
    k_s = params.k_s
    T_inf = params.T_inf
    
    assert T_new.shape == (Ntheta, Nr), f"Shape incorrecto: {T_new.shape}"
    assert T_old.shape == (Ntheta, Nr), f"Shape incorrecto: {T_old.shape}"
    
    # Extraer parámetros de la malla
    malla_aleta = mallas['aletas'][k_aleta]
    dr = malla_aleta['dr']
    dtheta = malla_aleta['dtheta']
    R = params.r  # Radio de la aleta (escalar)
    
    # Verificar que R coincide con el último nodo
    r_superficie = malla_aleta['r'][-1]
    assert np.isclose(r_superficie, R, rtol=1e-10), \
        f"Radio superficie {r_superficie} != R {R}"
    
    # Calcular números de Fourier
    Fo_r = alpha * dt / (dr**2)
    Fo_theta = alpha * dt  # Sin normalización espacial
    
    # Calcular coeficiente de acoplamiento
    beta_aire = h_aire * dr / k_s
    
    # Índice de la superficie
    j_sup = Nr - 1  # j=9
    
    # Aplicar Ecuación 14 para todos los ángulos internos
    for m in range(1, Ntheta - 1):
        # Temperatura en superficie (paso anterior)
        T_sup_old = T_old[m, j_sup]
        T_interior_old = T_old[m, j_sup - 1]  # j=8
        
        # Diferencia angular (SIN normalizar por dtheta²)
        diff_theta_2nd = (T_old[m+1, j_sup] - 2.0*T_old[m, j_sup] + T_old[m-1, j_sup])
        
        # Ecuación 14 (línea 209 del documento): BC Robin en r=R
        # CORRECCIÓN: El signo del término convectivo debe permitir calentamiento cuando T_∞ > T_s
        # T_{Nr,m}^{n+1} = T_{Nr,m}^n + 2·Fo_r·[(T_{Nr-1,m} - T_{Nr,m}) - β·(T_{Nr,m} - T_∞)]
        #                              + Fo_θ·(1/R²)·ΔΔθ
        # Equivalente a: ... + β·(T_∞ - T_{Nr,m}) para interpretación física directa
        T_new[m, j_sup] = (T_sup_old 
                          + 2.0 * Fo_r * ((T_interior_old - T_sup_old) 
                                         - beta_aire * (T_sup_old - T_inf))
                          + Fo_theta * (1.0 / (R * dtheta)**2) * diff_theta_2nd)
    
    # Validaciones de salida
    assert not np.isnan(T_new[:, j_sup]).any(), "NaN en superficie"
    assert not np.isinf(T_new[:, j_sup]).any(), "Inf en superficie"
    
    return T_new


def _aplicar_bc_theta_aleta(
    T_new: np.ndarray,
    T_old: np.ndarray,
    params: Parametros
) -> np.ndarray:
    """
    Aplica condiciones de frontera en los bordes angulares θ=0 y θ=π.
    
    Para el test aislado (sin acoplamiento con placa), usamos Neumann:
        ∂T/∂θ = 0  →  Extrapolación desde nodos interiores
    
    En la simulación completa, estos nodos se manejarán con continuidad
    en el módulo acoplamiento.py.
    
    Args:
        T_new: Campo actualizado parcialmente (Ntheta, Nr) [K]
        T_old: Campo en el paso anterior (Ntheta, Nr) [K]
        params: Instancia de Parametros
    
    Returns:
        T_new: Campo con BCs en m=0 y m=Ntheta-1 para todos los j [K]
    
    Notes:
        - m=0: θ=0 (interfaz plana inferior con placa)
        - m=Ntheta-1: θ=π (interfaz plana superior con placa)
        - Neumann: T[0,j] = T[1,j], T[Ntheta-1,j] = T[Ntheta-2,j]
        - Estas son BCs temporales para testing aislado
    """
    Ntheta = params.Ntheta_aleta
    Nr = params.Nr_aleta
    
    assert T_new.shape == (Ntheta, Nr), f"Shape incorrecto: {T_new.shape}"
    
    # BC en θ=0 (m=0): Neumann (extrapolación)
    T_new[0, :] = T_new[1, :]
    
    # BC en θ=π (m=Ntheta-1): Neumann (extrapolación)
    T_new[Ntheta-1, :] = T_new[Ntheta-2, :]
    
    # Validaciones
    assert not np.isnan(T_new[[0, -1], :]).any(), "NaN en bordes theta"
    assert not np.isinf(T_new[[0, -1], :]).any(), "Inf en bordes theta"
    
    return T_new


def actualizar_aleta(
    T_aleta_old: np.ndarray,
    params: Parametros,
    mallas: Dict,
    k_aleta: int,
    dt: float
) -> np.ndarray:
    """
    Actualiza el campo de temperatura de una aleta para un paso de tiempo.
    
    Integra todas las ecuaciones:
    - Ecuación 16: Centro r=0 (L'Hôpital)
    - Ecuación 15: Interior r>0 (FTCS cilíndrico)
    - Ecuación 14: Superficie r=R (Robin con aire)
    - BCs en θ=0 y θ=π (Neumann temporal)
    
    Args:
        T_aleta_old: Campo de temperatura en el paso anterior (Ntheta, Nr) [K]
        params: Instancia de Parametros
        mallas: Diccionario con todas las mallas
        k_aleta: Índice de la aleta (0, 1, o 2)
        dt: Paso de tiempo [s]
    
    Returns:
        T_aleta_new: Campo de temperatura actualizado (Ntheta, Nr) [K]
    
    Raises:
        AssertionError: Si las validaciones de estabilidad o física fallan
    
    Notes:
        - Orden de actualización:
          1. Validar estabilidad
          2. Actualizar centro (r=0)
          3. Actualizar interior (r>0)
          4. Aplicar BC superficie (r=R)
          5. Aplicar BCs angulares (θ=0, π)
          6. Validar salida
    
    References:
        - Algoritmo completo en todo/instrucciones_ecuaciones.md (línea 395-420)
    """
    # Validaciones de entrada
    Ntheta = params.Ntheta_aleta
    Nr = params.Nr_aleta
    alpha = params.alpha_s
    
    assert T_aleta_old.shape == (Ntheta, Nr), \
        f"Shape incorrecto: esperado ({Ntheta}, {Nr}), recibido {T_aleta_old.shape}"
    assert not np.isnan(T_aleta_old).any(), "Input contiene NaN"
    assert not np.isinf(T_aleta_old).any(), "Input contiene Inf"
    assert np.all((T_aleta_old >= 200) & (T_aleta_old <= 500)), \
        f"Temperaturas de entrada fuera de rango: [{T_aleta_old.min():.1f}, {T_aleta_old.max():.1f}] K"
    assert dt > 0, f"dt debe ser positivo: {dt}"
    assert k_aleta in [0, 1, 2], f"k_aleta debe ser 0, 1 o 2: {k_aleta}"
    
    # Extraer parámetros de la malla
    malla_aleta = mallas['aletas'][k_aleta]
    dr = malla_aleta['dr']
    dtheta = malla_aleta['dtheta']
    r_min = malla_aleta['r'][1]  # Primer nodo no-centro (j=1)
    
    # PASO 1: Validar estabilidad numérica
    # Fo_r es constante
    # Fo_θ = α·Δt (constante), pero el término completo Fo_θ·(1/r²Δθ²) es máximo en r_min
    Fo_r = alpha * dt / (dr**2)
    Fo_theta = alpha * dt  # Constante
    Fo_theta_efectivo_max = Fo_theta / ((r_min * dtheta)**2)  # Máximo en r_min
    Fo_total = Fo_r + Fo_theta_efectivo_max
    
    assert Fo_total < 0.5, \
        f"Criterio de estabilidad violado: Fo_r={Fo_r:.4f} + Fo_θ_eff(max)={Fo_theta_efectivo_max:.4f} = {Fo_total:.4f} >= 0.5"
    
    # PASO 2: Actualizar centro (r=0) - Ecuación 16
    T_centro_new = _actualizar_centro_aleta(T_aleta_old, Fo_r, params)
    
    # PASO 3: Actualizar nodos internos (r>0) - Ecuación 15
    T_new = _actualizar_interior_aleta(T_aleta_old, params, mallas, k_aleta, dt)
    
    # Insertar temperaturas del centro
    T_new[:, 0] = T_centro_new
    
    # PASO 4: Aplicar BC en superficie (r=R) - Ecuación 14
    T_new = _aplicar_bc_superficie_aleta(T_new, T_aleta_old, params, mallas, k_aleta, dt)
    
    # PASO 5: Aplicar BCs en θ=0 y θ=π (Neumann temporal)
    T_new = _aplicar_bc_theta_aleta(T_new, T_aleta_old, params)
    
    # PASO 6: Validaciones de salida
    assert T_new.shape == T_aleta_old.shape, "Shape cambió"
    assert not np.isnan(T_new).any(), "Output contiene NaN"
    assert not np.isinf(T_new).any(), "Output contiene Inf"
    assert np.all((T_new >= 200) & (T_new <= 500)), \
        f"Temperaturas de salida fuera de rango: [{T_new.min():.1f}, {T_new.max():.1f}] K"
    
    # Verificar que el cambio es razonable (< 50 K por paso)
    delta_T_max = np.abs(T_new - T_aleta_old).max()
    assert delta_T_max < 50.0, \
        f"Cambio de temperatura excesivo en un paso: {delta_T_max:.2f} K"
    
    return T_new


# =============================================================================
# SECCIÓN DE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SOLVER DE ALETAS - Sistema de Enfriamiento GPU")
    print("=" * 70)
    print()
    print("📐 Inicializando sistema...")
    print()
    
    # Crear parámetros y mallas
    from src.mallas import generar_todas_mallas
    
    params = Parametros()
    mallas = generar_todas_mallas(params)
    
    # Probar con la Aleta 1 (k=0, centrada en x=0.005m)
    k_aleta = 0
    malla_aleta = mallas['aletas'][k_aleta]
    
    print(f"🌡️  Inicializando campo de temperatura de la Aleta {k_aleta+1}...")
    T_aleta = inicializar_aleta(params, mallas, k_aleta)
    print(f"  ✅ Campo inicializado: {T_aleta.shape} = {T_aleta.shape[0] * T_aleta.shape[1]} nodos")
    print(f"  Temperatura inicial uniforme: {T_aleta[0,0] - 273.15:.1f}°C")
    print(f"  Rango: [{T_aleta.min() - 273.15:.1f}, {T_aleta.max() - 273.15:.1f}]°C")
    print()
    
    print("🌡️  Configurando condiciones del test...")
    print("  Aire ambiente: 23°C (constante, según contexto del proyecto)")
    print("  Aleta inicial: 23°C (equilibrio térmico inicial)")
    print("  NOTA: En este test aislado, la aleta NO está conectada a la placa.")
    print("  El calentamiento real vendrá de la placa caliente en la simulación completa.")
    print()
    
    # Usar parámetros estándar (aire a 23°C)
    params_test = Parametros()
    
    print("🧪 Parámetros de simulación:")
    
    # IMPORTANTE: Para aletas en coordenadas cilíndricas, Fo_θ es máximo en r_min
    # El dt de la placa (0.5 ms) es DEMASIADO GRANDE para aletas
    # Cálculo del dt máximo permitido:
    alpha = params_test.alpha_s
    dr = malla_aleta['dr']
    dtheta = malla_aleta['dtheta']
    r_min = malla_aleta['r'][1]  # Primer nodo después del centro
    
    # dt_max para estabilidad en aletas
    factor_estabilidad = alpha * (1.0/dr**2 + 1.0/((r_min * dtheta)**2))
    dt_max_aletas = 0.5 / factor_estabilidad
    
    # Usar dt con margen de seguridad (80% del máximo)
    dt = 0.8 * dt_max_aletas
    
    print(f"  ⚠️  NOTA: dt de la placa (0.5 ms) es inestable para aletas")
    print(f"  Calculando dt específico para coordenadas cilíndricas...")
    print(f"  dt_max(aletas) ≈ {dt_max_aletas:.2e} s")
    print(f"  Usando dt = {dt:.2e} s (80% del máximo)")
    print()
    
    Fo_r = alpha * dt / dr**2
    Fo_theta = alpha * dt  # Constante
    Fo_theta_efectivo_max = Fo_theta / ((r_min * dtheta)**2)  # Máximo en r_min
    Fo_total = Fo_r + Fo_theta_efectivo_max
    
    print(f"  - dt: {dt:.2e} s")
    print(f"  - dr: {dr:.2e} m")
    print(f"  - dθ: {dtheta:.4f} rad ({np.degrees(dtheta):.1f}°)")
    print(f"  - R: {params_test.r:.4f} m")
    print(f"  - r_min: {r_min:.2e} m (primer nodo)")
    print(f"  - Fo_r: {Fo_r:.4f}")
    print(f"  - Fo_θ_eff(max): {Fo_theta_efectivo_max:.4f}")
    print(f"  - Fo_total: {Fo_total:.4f} (debe ser < 0.5)")
    print(f"  - α (Al): {alpha:.2e} m²/s")
    print()
    
    # Tiempo característico para aletas (R²/α)
    tau_aleta = params_test.r**2 / alpha
    print(f"  Tiempo característico difusión τ = R²/α ≈ {tau_aleta:.3f} s")
    print()
    
    # Simular 1 segundo (suficiente para ~4τ, adecuado para test inicial)
    t_final = 1.0  # segundos
    num_pasos = int(t_final / dt)
    print(f"⏱️  Ejecutando {num_pasos} pasos de tiempo (t_final = {t_final:.1f} s ≈ {t_final/tau_aleta:.1f}τ)...")
    print(f"  NOTA: Esto toma ~{num_pasos/1000:.0f}k iteraciones debido al dt pequeño requerido")
    print(f"  por la singularidad en r→0 en coordenadas cilíndricas.")
    print()
    
    # Calcular intervalos de progreso (10 puntos distribuidos logarítmicamente)
    intervalos = [0]
    for i in range(1, 10):
        intervalos.append(int(num_pasos * (10**i / 10**10)))
    intervalos.append(num_pasos - 1)
    intervalos = sorted(set(intervalos))  # Eliminar duplicados y ordenar
    
    for n in range(num_pasos):
        T_aleta = actualizar_aleta(T_aleta, params_test, mallas, k_aleta, dt)
        
        # Mostrar progreso en intervalos calculados
        if n in intervalos:
            t_actual = (n + 1) * dt
            T_min = T_aleta.min() - 273.15
            T_max = T_aleta.max() - 273.15
            T_centro = T_aleta[0, 0] - 273.15  # Centro (r=0)
            T_sup = T_aleta[:, -1].mean() - 273.15  # Superficie promedio
            
            print(f"    t = {t_actual:.2e} s | T_min = {T_min:.2f}°C | T_max = {T_max:.2f}°C | T_centro = {T_centro:.2f}°C")
            print(f"      T_superficie(promedio) = {T_sup:.2f}°C")
    
    print()
    print("=" * 70)
    print("✅ Solver de aletas funcionando correctamente")
    print("=" * 70)
    print()
    
    # Estadísticas finales
    T_min_final = T_aleta.min() - 273.15
    T_max_final = T_aleta.max() - 273.15
    T_mean_final = T_aleta.mean() - 273.15
    T_centro_final = T_aleta[0, 0] - 273.15
    T_sup_final = T_aleta[:, -1].mean() - 273.15
    
    print("📊 Estadísticas finales:")
    print(f"  Temperatura mínima: {T_min_final:.2f}°C")
    print(f"  Temperatura máxima: {T_max_final:.2f}°C")
    print(f"  Temperatura promedio: {T_mean_final:.2f}°C")
    print(f"  Temperatura en centro (r=0): {T_centro_final:.2f}°C")
    print(f"  Temperatura en superficie (r=R): {T_sup_final:.2f}°C")
    print()
    
    # Interpretación física
    print("🔬 Interpretación física:")
    delta_T_calentamiento = T_mean_final - 23.0
    print(f"  Calentamiento total: {delta_T_calentamiento:.2f}°C (desde 23°C)")
    print(f"  Gradiente radial: {T_sup_final - T_centro_final:.2f}°C")
    print()
    
    if T_sup_final > T_centro_final:
        print("  ✓ Superficie más caliente que centro (convección desde aire)")
    
    print()

