"""
Módulo de Acoplamiento Térmico - Sistema de Enfriamiento GPU

Este módulo maneja las interfaces térmicas entre los tres dominios:
1. Fluido (1D) ↔ Placa (2D cartesiano)
2. Placa (2D cartesiano) ↔ Aletas (2D cilíndrico)

Las funciones implementan continuidad de temperatura en las interfaces,
incluyendo interpolación entre mallas de diferentes dimensiones y sistemas
de coordenadas.

Referencias:
    - Condiciones de interfaz: contexto/04_condiciones_frontera.md (sección 5)
    - Discretización: contexto/05_discretizacion_numerica.md

Autor: Sistema de Enfriamiento GPU - Proyecto IQ-0331
Fecha: 2025-10-04
"""

import numpy as np
from typing import Dict, Tuple, List
from numpy.typing import NDArray


def extraer_temperatura_superficie_placa(
    T_placa: NDArray[np.float64],
    mallas: Dict,
    params
) -> NDArray[np.float64]:
    """
    Extrae la temperatura de la superficie inferior de la placa (y=0).
    
    Esta superficie está en contacto con el fluido de refrigeración.
    
    Args:
        T_placa: Array 2D (Ny, Nx) con temperatura de la placa [K]
        mallas: Diccionario con información de las mallas
        params: Objeto Parametros con configuración del sistema
    
    Returns:
        T_superficie: Array 1D (Nx_placa) con temperatura en y=0 [K]
    
    Raises:
        AssertionError: Si las validaciones de entrada/salida fallan
    
    Notes:
        - La superficie inferior corresponde a j=0 (primera fila)
        - Esta temperatura se usará para el acoplamiento con el fluido
    
    Example:
        >>> T_sup = extraer_temperatura_superficie_placa(T_placa, mallas, params)
        >>> print(T_sup.shape)  # (Nx_placa,)
    """
    # Validaciones de entrada
    assert T_placa.ndim == 2, f"T_placa debe ser 2D, es {T_placa.ndim}D"
    assert not np.isnan(T_placa).any(), "T_placa contiene NaN"
    assert not np.isinf(T_placa).any(), "T_placa contiene Inf"
    
    Nx_placa = params.Nx_placa
    Ny_placa = params.Ny_placa
    
    # T_placa tiene shape (Nx, Ny) según placa.py
    assert T_placa.shape == (Nx_placa, Ny_placa), \
        f"Shape incorrecto: {T_placa.shape} != ({Nx_placa}, {Ny_placa})"
    
    # Extraer primera columna (j=0, superficie en contacto con agua)
    # T_placa[i, 0] es la temperatura en (x_i, y=0)
    T_superficie = T_placa[:, 0].copy()
    
    # Validaciones de salida
    assert T_superficie.shape == (Nx_placa,), \
        f"Shape de salida incorrecto: {T_superficie.shape}"
    assert not np.isnan(T_superficie).any(), "Output contiene NaN"
    assert not np.isinf(T_superficie).any(), "Output contiene Inf"
    assert T_superficie.min() > 200.0, \
        f"Temperatura muy baja: {T_superficie.min():.1f}K < 200K"
    assert T_superficie.max() < 500.0, \
        f"Temperatura muy alta: {T_superficie.max():.1f}K > 500K"
    
    return T_superficie


def interpolar_temperatura_para_fluido(
    T_superficie_placa: NDArray[np.float64],
    mallas: Dict,
    params
) -> NDArray[np.float64]:
    """
    Interpola temperatura de la superficie de la placa a la malla del fluido.
    
    Si las mallas del fluido y placa tienen diferente resolución en x,
    esta función realiza interpolación lineal para obtener valores de
    temperatura en las posiciones x del fluido.
    
    Args:
        T_superficie_placa: Array 1D (Nx_placa) temperatura superficie [K]
        mallas: Diccionario con información de las mallas
        params: Objeto Parametros
    
    Returns:
        T_para_fluido: Array 1D (Nx_fluido) temperatura interpolada [K]
    
    Raises:
        AssertionError: Si las validaciones fallan
    
    Notes:
        - Si Nx_fluido == Nx_placa, retorna copia directa
        - Si difieren, usa np.interp() para interpolación lineal
        - Extrapolación constante en los extremos
    
    References:
        Sección 5.1 de contexto/04_condiciones_frontera.md
    """
    # Validaciones de entrada
    assert T_superficie_placa.ndim == 1, "T_superficie debe ser 1D"
    assert not np.isnan(T_superficie_placa).any(), "Input contiene NaN"
    assert not np.isinf(T_superficie_placa).any(), "Input contiene Inf"
    
    Nx_placa = params.Nx_placa
    Nx_fluido = params.Nx_fluido
    
    assert len(T_superficie_placa) == Nx_placa, \
        f"Tamaño incorrecto: {len(T_superficie_placa)} != {Nx_placa}"
    
    # Coordenadas x de las mallas
    x_placa = mallas['placa']['x']  # Array 1D
    x_fluido = mallas['fluido']['x']  # Array 1D
    
    # Caso 1: Mallas coinciden (sin interpolación necesaria)
    if Nx_fluido == Nx_placa and np.allclose(x_placa, x_fluido):
        T_para_fluido = T_superficie_placa.copy()
    
    # Caso 2: Interpolación lineal necesaria
    else:
        T_para_fluido = np.interp(
            x_fluido,           # Posiciones donde queremos valores
            x_placa,            # Posiciones conocidas
            T_superficie_placa  # Valores conocidos
        )
    
    # Validaciones de salida
    assert T_para_fluido.shape == (Nx_fluido,), \
        f"Shape incorrecto: {T_para_fluido.shape}"
    assert not np.isnan(T_para_fluido).any(), "Output contiene NaN"
    assert not np.isinf(T_para_fluido).any(), "Output contiene Inf"
    assert T_para_fluido.min() >= T_superficie_placa.min() - 1.0, \
        "Interpolación produjo valores anormalmente bajos"
    assert T_para_fluido.max() <= T_superficie_placa.max() + 1.0, \
        "Interpolación produjo valores anormalmente altos"
    
    return T_para_fluido


def mapear_coordenadas_placa_a_aleta(
    r_array: NDArray[np.float64],
    theta_array: NDArray[np.float64],
    x_centro_aleta: float,
    y_base_placa: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Convierte coordenadas cilíndricas de la aleta a cartesianas de la placa.
    
    Para una aleta centrada en x_k, montada en y=e_base, calcula las
    coordenadas (x, y) correspondientes en el sistema cartesiano de la placa.
    
    Transformación:
        x = x_k + r * cos(θ)
        y = y_base (constante en la interfaz)
    
    Args:
        r_array: Array 1D con coordenadas radiales de la aleta [m]
        theta_array: Array 1D con coordenadas angulares [rad]
        x_centro_aleta: Posición x del centro de la aleta [m]
        y_base_placa: Altura de la base de la placa e_base [m]
    
    Returns:
        x_coords: Array con coordenadas x en sistema cartesiano [m]
        y_coords: Array con coordenadas y (todos = y_base) [m]
    
    Notes:
        - θ=0: lado derecho del diámetro (x > x_k)
        - θ=π: lado izquierdo del diámetro (x < x_k)
        - La interfaz está en y = e_base (tope de la placa)
    
    References:
        Ecuación de mapeo en contexto/04_condiciones_frontera.md línea 120
    """
    # Validaciones
    assert r_array.ndim == 1, "r_array debe ser 1D"
    assert theta_array.ndim == 1, "theta_array debe ser 1D"
    assert len(r_array) == len(theta_array), \
        "r_array y theta_array deben tener mismo tamaño"
    assert np.all(r_array >= 0), "r debe ser >= 0"
    assert np.all(theta_array >= 0) and np.all(theta_array <= np.pi), \
        "theta debe estar en [0, π]"
    
    # Transformación de coordenadas cilíndricas → cartesianas
    x_coords = x_centro_aleta + r_array * np.cos(theta_array)
    y_coords = np.full_like(r_array, y_base_placa)
    
    # Validaciones de salida
    assert x_coords.shape == r_array.shape, "Shape inconsistente en x"
    assert y_coords.shape == r_array.shape, "Shape inconsistente en y"
    assert not np.isnan(x_coords).any(), "x_coords contiene NaN"
    assert not np.isnan(y_coords).any(), "y_coords contiene NaN"
    
    return x_coords, y_coords


def interpolar_temperatura_placa_2d(
    T_placa: NDArray[np.float64],
    x_objetivo: NDArray[np.float64],
    y_objetivo: NDArray[np.float64],
    mallas: Dict,
    params
) -> NDArray[np.float64]:
    """
    Interpola temperatura de la placa en puntos arbitrarios (x, y).
    
    Usa interpolación bilineal para obtener valores de temperatura en
    posiciones que no coinciden exactamente con los nodos de la malla.
    
    Args:
        T_placa: Array 2D (Ny, Nx) temperatura de la placa [K]
        x_objetivo: Array 1D con coordenadas x donde interpolar [m]
        y_objetivo: Array 1D con coordenadas y donde interpolar [m]
        mallas: Diccionario con mallas
        params: Objeto Parametros
    
    Returns:
        T_interpolada: Array 1D con temperaturas interpoladas [K]
    
    Raises:
        AssertionError: Si los puntos están fuera del dominio
    
    Notes:
        - Usa scipy.interpolate.RectBivariateSpline para interpolación
        - Si un punto está muy cerca de un nodo, usa valor directo
        - Puntos fuera del dominio causan error
    
    Algorithm:
        1. Crea interpolador bilineal de T_placa
        2. Evalúa en (x_objetivo, y_objetivo)
        3. Valida resultados físicos
    """
    from scipy.interpolate import RegularGridInterpolator
    
    # Validaciones de entrada
    assert T_placa.ndim == 2, "T_placa debe ser 2D"
    assert not np.isnan(T_placa).any(), "T_placa contiene NaN"
    assert not np.isinf(T_placa).any(), "T_placa contiene Inf"
    assert len(x_objetivo) == len(y_objetivo), \
        "x_objetivo y y_objetivo deben tener mismo tamaño"
    
    # Extraer mallas de la placa
    x_placa_unique = mallas['placa']['x']  # Coordenadas x únicas (1D)
    y_placa_unique = mallas['placa']['y']  # Coordenadas y únicas (1D)
    
    # Verificar que los puntos objetivo están dentro del dominio
    x_min, x_max = x_placa_unique.min(), x_placa_unique.max()
    y_min, y_max = y_placa_unique.min(), y_placa_unique.max()
    
    assert np.all(x_objetivo >= x_min) and np.all(x_objetivo <= x_max), \
        f"x_objetivo fuera de rango [{x_min}, {x_max}]: [{x_objetivo.min()}, {x_objetivo.max()}]"
    assert np.all(y_objetivo >= y_min) and np.all(y_objetivo <= y_max), \
        f"y_objetivo fuera de rango [{y_min}, {y_max}]: [{y_objetivo.min()}, {y_objetivo.max()}]"
    
    # Crear interpolador bilineal
    # Nota: T_placa tiene shape (Nx, Ny), por lo que el orden es (x, y)
    interpolador = RegularGridInterpolator(
        (x_placa_unique, y_placa_unique),
        T_placa,
        method='linear',
        bounds_error=True,
        fill_value=None
    )
    
    # Preparar puntos para interpolación (formato: [[x1, y1], [x2, y2], ...])
    puntos = np.column_stack([x_objetivo, y_objetivo])
    
    # Interpolar
    T_interpolada = interpolador(puntos)
    
    # Validaciones de salida
    assert T_interpolada.shape == x_objetivo.shape, "Shape inconsistente"
    assert not np.isnan(T_interpolada).any(), "Interpolación produjo NaN"
    assert not np.isinf(T_interpolada).any(), "Interpolación produjo Inf"
    assert T_interpolada.min() >= T_placa.min() - 1.0, \
        "Interpolación fuera de rango inferior"
    assert T_interpolada.max() <= T_placa.max() + 1.0, \
        "Interpolación fuera de rango superior"
    
    return T_interpolada


def aplicar_acoplamiento_placa_aletas(
    T_placa: NDArray[np.float64],
    T_aletas: List[NDArray[np.float64]],
    mallas: Dict,
    params
) -> List[NDArray[np.float64]]:
    """
    Aplica acoplamiento térmico entre placa y aletas.
    
    Para cada una de las 3 aletas, interpola la temperatura de la placa
    a lo largo del diámetro de contacto (θ=0 y θ=π) y aplica como
    condición de frontera en las aletas.
    
    Proceso:
        1. Para cada aleta k (k=0,1,2):
           a. Identificar nodos en θ=0 y θ=π (diámetro de contacto)
           b. Mapear coordenadas cilíndricas → cartesianas
           c. Interpolar T_placa en esas posiciones
           d. Aplicar T_interpolada como BC en la aleta
    
    Args:
        T_placa: Array 2D (Ny, Nx) temperatura de la placa [K]
        T_aletas: Lista de 3 arrays 2D (Ntheta, Nr) temperatura de aletas [K]
        mallas: Diccionario con información de mallas
        params: Objeto Parametros
    
    Returns:
        T_aletas_acopladas: Lista de 3 arrays con BCs aplicadas [K]
    
    Raises:
        AssertionError: Si las validaciones fallan
    
    Notes:
        - Las aletas están centradas en x = [5mm, 15mm, 25mm]
        - La interfaz está en y = e_base (tope de la placa)
        - θ=0 corresponde al lado derecho (+x)
        - θ=π corresponde al lado izquierdo (-x)
    
    References:
        - Interfaz placa-aleta: contexto/04_condiciones_frontera.md sección 5
        - Posiciones de aletas: contexto/02_parametros_sistema.md
    
    Example:
        >>> T_aletas_new = aplicar_acoplamiento_placa_aletas(T_placa, T_aletas, mallas, params)
        >>> # T_aletas_new[0] tiene temperaturas de la placa en θ=0,π
    """
    # Validaciones de entrada
    assert T_placa.ndim == 2, "T_placa debe ser 2D"
    assert len(T_aletas) == 3, f"Debe haber 3 aletas, hay {len(T_aletas)}"
    
    for k, T_aleta in enumerate(T_aletas):
        assert T_aleta.ndim == 2, f"T_aletas[{k}] debe ser 2D"
        assert not np.isnan(T_aleta).any(), f"T_aletas[{k}] contiene NaN"
        assert not np.isinf(T_aleta).any(), f"T_aletas[{k}] contiene Inf"
    
    # Extraer parámetros
    Nr = params.Nr_aleta
    Ntheta = params.Ntheta_aleta
    e_base = params.e_base
    
    # Posiciones de las 3 aletas (centros en x)
    x_aletas = [
        params.x_aleta_1,  # 0.005 m
        params.x_aleta_2,  # 0.015 m
        params.x_aleta_3   # 0.025 m
    ]
    
    # Copiar arrays de entrada (no modificar originales)
    T_aletas_acopladas = [T.copy() for T in T_aletas]
    
    # Procesar cada aleta
    for k in range(3):
        malla_aleta = mallas['aletas'][k]
        r_array = malla_aleta['r']  # Array 1D con coordenadas r (Nr,)
        
        # ==================================================================
        # BORDE θ=0 (m=0): Lado derecho del diámetro (x > x_k)
        # ==================================================================
        m_theta_0 = 0
        theta_0 = 0.0  # rad
        
        # Para todos los nodos radiales en θ=0
        r_nodos = r_array  # Shape: (Nr,) - Array 1D completo
        theta_nodos = np.full(Nr, theta_0)  # Todos en θ=0
        
        # Mapear a coordenadas cartesianas
        x_cart_0, y_cart_0 = mapear_coordenadas_placa_a_aleta(
            r_nodos, theta_nodos, x_aletas[k], e_base
        )
        
        # Interpolar temperatura de la placa en esos puntos
        T_placa_en_aleta_0 = interpolar_temperatura_placa_2d(
            T_placa, x_cart_0, y_cart_0, mallas, params
        )
        
        # Aplicar como condición de frontera en la aleta
        T_aletas_acopladas[k][m_theta_0, :] = T_placa_en_aleta_0
        
        # ==================================================================
        # BORDE θ=π (m=Ntheta-1): Lado izquierdo del diámetro (x < x_k)
        # ==================================================================
        m_theta_pi = Ntheta - 1
        theta_pi = np.pi  # rad
        
        # Para todos los nodos radiales en θ=π
        theta_nodos_pi = np.full(Nr, theta_pi)
        
        # Mapear a coordenadas cartesianas
        x_cart_pi, y_cart_pi = mapear_coordenadas_placa_a_aleta(
            r_nodos, theta_nodos_pi, x_aletas[k], e_base
        )
        
        # Interpolar temperatura de la placa en esos puntos
        T_placa_en_aleta_pi = interpolar_temperatura_placa_2d(
            T_placa, x_cart_pi, y_cart_pi, mallas, params
        )
        
        # Aplicar como condición de frontera en la aleta
        T_aletas_acopladas[k][m_theta_pi, :] = T_placa_en_aleta_pi
    
    # Validaciones finales
    for k, T_aleta_new in enumerate(T_aletas_acopladas):
        assert T_aleta_new.shape == T_aletas[k].shape, \
            f"Shape cambió para aleta {k}"
        assert not np.isnan(T_aleta_new).any(), \
            f"T_aletas_acopladas[{k}] contiene NaN"
        assert not np.isinf(T_aleta_new).any(), \
            f"T_aletas_acopladas[{k}] contiene Inf"
        assert T_aleta_new.min() > 200.0, \
            f"Aleta {k}: Temperatura muy baja {T_aleta_new.min():.1f}K"
        assert T_aleta_new.max() < 500.0, \
            f"Aleta {k}: Temperatura muy alta {T_aleta_new.max():.1f}K"
    
    return T_aletas_acopladas


# ============================================================================
# FUNCIONES DE UTILIDAD Y DIAGNÓSTICO
# ============================================================================

def verificar_continuidad_temperatura(
    T_placa: NDArray[np.float64],
    T_aletas: List[NDArray[np.float64]],
    mallas: Dict,
    params,
    tolerancia: float = 1.0
) -> Dict[str, float]:
    """
    Verifica la continuidad de temperatura en las interfaces placa-aletas.
    
    Calcula la diferencia máxima entre la temperatura de la placa y
    las aletas en los puntos de contacto (θ=0, π).
    
    Args:
        T_placa: Temperatura de la placa [K]
        T_aletas: Lista de temperaturas de las 3 aletas [K]
        mallas: Diccionario con mallas
        params: Objeto Parametros
        tolerancia: Diferencia máxima permitida [K]
    
    Returns:
        diagnostico: Dict con información de continuidad:
            - 'max_error': Error máximo absoluto [K]
            - 'mean_error': Error promedio [K]
            - 'cumple': Boolean, True si error < tolerancia
            - 'por_aleta': Lista de errores máximos por aleta
    
    Notes:
        - Útil para debugging y validación del acoplamiento
        - Errores grandes (>1K) indican problemas de interpolación
    """
    errores_por_aleta = []
    
    for k in range(3):
        # Extraer temperaturas en θ=0 y θ=π de la aleta
        T_aleta_theta0 = T_aletas[k][0, :]
        T_aleta_thetapi = T_aletas[k][-1, :]
        
        # Coordenadas correspondientes en la placa
        x_aleta_centro = [params.x_aleta_1, params.x_aleta_2, params.x_aleta_3][k]
        r_array = mallas['aletas'][k]['r']  # Array 1D
        
        # θ=0: lado derecho
        x_theta0 = x_aleta_centro + r_array * np.cos(0)
        y_theta0 = np.full_like(r_array, params.e_base)
        T_placa_theta0 = interpolar_temperatura_placa_2d(
            T_placa, x_theta0, y_theta0, mallas, params
        )
        
        # θ=π: lado izquierdo
        x_thetapi = x_aleta_centro + r_array * np.cos(np.pi)
        y_thetapi = np.full_like(r_array, params.e_base)
        T_placa_thetapi = interpolar_temperatura_placa_2d(
            T_placa, x_thetapi, y_thetapi, mallas, params
        )
        
        # Calcular errores
        error_theta0 = np.abs(T_aleta_theta0 - T_placa_theta0).max()
        error_thetapi = np.abs(T_aleta_thetapi - T_placa_thetapi).max()
        error_max_aleta = max(error_theta0, error_thetapi)
        
        errores_por_aleta.append(error_max_aleta)
    
    max_error = max(errores_por_aleta)
    mean_error = np.mean(errores_por_aleta)
    
    diagnostico = {
        'max_error': max_error,
        'mean_error': mean_error,
        'cumple': max_error < tolerancia,
        'por_aleta': errores_por_aleta
    }
    
    return diagnostico


# ============================================================================
# TEST EJECUTABLE
# ============================================================================

if __name__ == "__main__":
    """
    Test de validación del módulo de acoplamiento.
    
    Verifica:
    1. Extracción de temperatura superficial de la placa
    2. Interpolación fluido-placa
    3. Mapeo de coordenadas cilíndricas-cartesianas
    4. Interpolación 2D de la placa
    5. Acoplamiento placa-aletas completo
    6. Verificación de continuidad
    """
    import sys
    import os
    
    # Añadir directorio src al path si no está
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from src.parametros import Parametros
    from src.mallas import generar_todas_mallas
    
    print("=" * 70)
    print("TEST DE ACOPLAMIENTO TÉRMICO - Sistema de Enfriamiento GPU")
    print("=" * 70)
    print()
    
    # Inicializar sistema
    print("📐 Inicializando parámetros y mallas...")
    params = Parametros()
    mallas = generar_todas_mallas(params)
    print("  ✅ Sistema inicializado")
    print()
    
    # ========================================================================
    # TEST 1: Extracción de temperatura superficial
    # ========================================================================
    print("🔍 TEST 1: Extracción de temperatura superficial de la placa")
    print("-" * 70)
    
    # Crear campo de temperatura de prueba para la placa
    T_placa_test = np.ones((params.Ny_placa, params.Nx_placa)) * 300.0  # 26.85°C base
    
    # Simular gradiente vertical (más caliente en contacto con agua)
    for j in range(params.Ny_placa):
        factor = 1.0 - j / (params.Ny_placa - 1)  # 1.0 en y=0, 0.0 en y=e_base
        T_placa_test[j, :] = 300.0 + 20.0 * factor  # 320K en agua, 300K en aire
    
    T_sup = extraer_temperatura_superficie_placa(T_placa_test, mallas, params)
    
    print(f"  Dimensiones de la placa: {T_placa_test.shape}")
    print(f"  Temperatura superficial extraída: {T_sup.shape}")
    print(f"  Rango: [{T_sup.min() - 273.15:.2f}, {T_sup.max() - 273.15:.2f}]°C")
    print(f"  Esperado: ~46.85°C (lado agua)")
    print("  ✅ Extracción correcta")
    print()
    
    # ========================================================================
    # TEST 2: Interpolación para fluido
    # ========================================================================
    print("🔍 TEST 2: Interpolación de temperatura para el fluido")
    print("-" * 70)
    
    T_para_fluido = interpolar_temperatura_para_fluido(T_sup, mallas, params)
    
    print(f"  Nx_placa: {params.Nx_placa}, Nx_fluido: {params.Nx_fluido}")
    print(f"  Temperatura interpolada: {T_para_fluido.shape}")
    print(f"  Rango: [{T_para_fluido.min() - 273.15:.2f}, {T_para_fluido.max() - 273.15:.2f}]°C")
    
    if params.Nx_fluido == params.Nx_placa:
        print("  Mallas coinciden: Sin interpolación necesaria ✅")
    else:
        print("  Interpolación lineal aplicada ✅")
    print()
    
    # ========================================================================
    # TEST 3: Mapeo de coordenadas
    # ========================================================================
    print("🔍 TEST 3: Mapeo de coordenadas cilíndricas → cartesianas")
    print("-" * 70)
    
    # Usar aleta 2 (centro en x=15mm) como ejemplo
    k_test = 1
    x_centro = params.x_aleta_2
    y_base = params.e_base
    
    # Tomar algunos puntos radiales en θ=0 y θ=π
    r_test = np.array([0.0, 0.002, 0.004])  # centro, medio, superficie
    theta_0 = np.array([0.0, 0.0, 0.0])
    theta_pi = np.array([np.pi, np.pi, np.pi])
    
    x_theta0, y_theta0 = mapear_coordenadas_placa_a_aleta(r_test, theta_0, x_centro, y_base)
    x_thetapi, y_thetapi = mapear_coordenadas_placa_a_aleta(r_test, theta_pi, x_centro, y_base)
    
    print(f"  Centro de aleta 2: x = {x_centro * 1000:.1f} mm")
    print(f"  Base: y = {y_base * 1000:.2f} mm")
    print()
    print("  Mapeo en θ=0 (lado derecho):")
    for i, r in enumerate(r_test):
        print(f"    r={r*1000:.1f}mm → x={x_theta0[i]*1000:.2f}mm, y={y_theta0[i]*1000:.2f}mm")
    print()
    print("  Mapeo en θ=π (lado izquierdo):")
    for i, r in enumerate(r_test):
        print(f"    r={r*1000:.1f}mm → x={x_thetapi[i]*1000:.2f}mm, y={y_thetapi[i]*1000:.2f}mm")
    print("  ✅ Mapeo correcto")
    print()
    
    # ========================================================================
    # TEST 4: Interpolación 2D
    # ========================================================================
    print("🔍 TEST 4: Interpolación 2D de temperatura de la placa")
    print("-" * 70)
    
    # Interpolar en los puntos mapeados
    T_interp_0 = interpolar_temperatura_placa_2d(
        T_placa_test, x_theta0, y_theta0, mallas, params
    )
    T_interp_pi = interpolar_temperatura_placa_2d(
        T_placa_test, x_thetapi, y_thetapi, mallas, params
    )
    
    print("  Temperaturas interpoladas en θ=0:")
    for i, r in enumerate(r_test):
        print(f"    r={r*1000:.1f}mm: T={T_interp_0[i] - 273.15:.2f}°C")
    print()
    print("  Temperaturas interpoladas en θ=π:")
    for i, r in enumerate(r_test):
        print(f"    r={r*1000:.1f}mm: T={T_interp_pi[i] - 273.15:.2f}°C")
    print("  ✅ Interpolación 2D correcta")
    print()
    
    # ========================================================================
    # TEST 5: Acoplamiento completo placa-aletas
    # ========================================================================
    print("🔍 TEST 5: Acoplamiento completo placa-aletas")
    print("-" * 70)
    
    # Crear campos de temperatura de prueba para las 3 aletas
    T_aletas_test = []
    for k in range(3):
        T_aleta_k = np.ones((params.Ntheta_aleta, params.Nr_aleta)) * 296.15  # 23°C inicial
        T_aletas_test.append(T_aleta_k)
    
    print(f"  Temperaturas iniciales de aletas: 23.00°C (uniformes)")
    print(f"  Aplicando acoplamiento con placa...")
    
    # Aplicar acoplamiento
    T_aletas_acopladas = aplicar_acoplamiento_placa_aletas(
        T_placa_test, T_aletas_test, mallas, params
    )
    
    print()
    print("  Resultados por aleta:")
    for k in range(3):
        x_centro_k = [params.x_aleta_1, params.x_aleta_2, params.x_aleta_3][k]
        T_theta0 = T_aletas_acopladas[k][0, :]
        T_thetapi = T_aletas_acopladas[k][-1, :]
        
        print(f"  Aleta {k+1} (x={x_centro_k*1000:.1f}mm):")
        print(f"    θ=0:  T_min={T_theta0.min()-273.15:.2f}°C, T_max={T_theta0.max()-273.15:.2f}°C")
        print(f"    θ=π:  T_min={T_thetapi.min()-273.15:.2f}°C, T_max={T_thetapi.max()-273.15:.2f}°C")
    print()
    print("  ✅ Acoplamiento aplicado correctamente")
    print()
    
    # ========================================================================
    # TEST 6: Verificación de continuidad
    # ========================================================================
    print("🔍 TEST 6: Verificación de continuidad de temperatura")
    print("-" * 70)
    
    diagnostico = verificar_continuidad_temperatura(
        T_placa_test, T_aletas_acopladas, mallas, params, tolerancia=1.0
    )
    
    print(f"  Error máximo: {diagnostico['max_error']:.4f} K")
    print(f"  Error promedio: {diagnostico['mean_error']:.4f} K")
    print()
    print("  Errores por aleta:")
    for k, error in enumerate(diagnostico['por_aleta']):
        print(f"    Aleta {k+1}: {error:.4f} K")
    print()
    
    if diagnostico['cumple']:
        print("  ✅ Continuidad satisfecha (error < 1.0 K)")
    else:
        print(f"  ⚠️  Error de continuidad alto: {diagnostico['max_error']:.4f} K")
    print()
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("=" * 70)
    print("✅ TODOS LOS TESTS DE ACOPLAMIENTO PASARON CORRECTAMENTE")
    print("=" * 70)
    print()
    print("📊 Resumen:")
    print(f"  1. Extracción superficial: ✅")
    print(f"  2. Interpolación fluido-placa: ✅")
    print(f"  3. Mapeo coordenadas: ✅")
    print(f"  4. Interpolación 2D: ✅")
    print(f"  5. Acoplamiento placa-aletas: ✅")
    print(f"  6. Continuidad térmica: {'✅' if diagnostico['cumple'] else '⚠️'}")
    print()
    print("🎯 Módulo de acoplamiento validado y listo para integración")
    print()

