"""
Módulo de solver de la placa para el sistema de enfriamiento GPU.

Este módulo implementa el solver 2D de la placa base usando el esquema
FTCS (Forward-Time Central-Space) para la ecuación de difusión de calor.

La ecuación implementada es:
    ∂T/∂t = α(∂²T/∂x² + ∂²T/∂y²)

Con condiciones de frontera Robin en las superficies:
- y=0: Convección con agua (h_agua)
- y=e_base: Convección con aire (h_aire)
- x=0, x=L_x: Aislamiento o simetría

Referencias:
- Ecuación: contexto/03_ecuaciones_gobernantes.md - Ecuación 2
- Discretización: contexto/05_discretizacion_numerica.md - Secciones 4.2 y 4.3
- Parámetros: contexto/02_parametros_sistema.md
"""

import numpy as np
from typing import Dict
from .parametros import Parametros


def inicializar_placa(params: Parametros, mallas: Dict) -> np.ndarray:
    """
    Inicializa el campo de temperatura de la placa.
    
    La placa parte con temperatura uniforme igual a la temperatura inicial
    del sistema (23°C).
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
        mallas (dict): Diccionario con todas las mallas del sistema
    
    Returns:
        ndarray: Array 2D con temperatura inicial de la placa [K]
            Shape: (Nx_placa, Ny_placa)
    
    Notes:
        - Temperatura inicial: 23°C (296.15 K) uniforme
        - Indexación: T_placa[i,j] donde i es x, j es y
        - j=0: interfaz con agua (y=0)
        - j=Ny-1: superficie superior expuesta al aire (y=e_base)
    
    References:
        Ver contexto/02_parametros_sistema.md - Tabla II
    """
    # Extraer parámetros
    Nx = params.Nx_placa
    Ny = params.Ny_placa
    T_inicial = params.T_inicial  # 296.15 K (23°C)
    
    # Crear array 2D con temperatura inicial uniforme
    T_placa = np.full((Nx, Ny), T_inicial, dtype=np.float64)
    
    # Validaciones
    assert T_placa.shape == (Nx, Ny), \
        f"Shape incorrecto: {T_placa.shape} != ({Nx}, {Ny})"
    assert not np.isnan(T_placa).any(), "Inicialización contiene NaN"
    assert not np.isinf(T_placa).any(), "Inicialización contiene Inf"
    assert 200 < T_placa.min() < 400, \
        f"Temperatura inicial fuera de rango: {T_placa.min():.2f} K"
    
    return T_placa


def _interpolar_fluido_a_placa(T_fluido: np.ndarray,
                                x_fluido: np.ndarray,
                                x_placa: np.ndarray) -> np.ndarray:
    """
    Interpola temperatura del fluido a los nodos x de la placa.
    
    Esta función auxiliar maneja el caso donde las mallas del fluido
    y la placa pueden tener diferente número de nodos en x.
    
    Args:
        T_fluido (ndarray): Temperatura del fluido [K]
            Shape: (Nx_fluido,)
        x_fluido (ndarray): Coordenadas x del fluido [m]
            Shape: (Nx_fluido,)
        x_placa (ndarray): Coordenadas x de la placa [m]
            Shape: (Nx_placa,)
    
    Returns:
        ndarray: Temperatura interpolada en nodos x de la placa [K]
            Shape: (Nx_placa,)
    
    Notes:
        En este caso Nx_fluido = Nx_placa = 60, pero la función
        es general por si se cambian las resoluciones.
    """
    if len(T_fluido) == len(x_placa):
        # Mallas coinciden, no necesita interpolación
        return T_fluido.copy()
    else:
        # Interpolación lineal
        T_interpolado = np.interp(x_placa, x_fluido, T_fluido)
        
        # Validaciones
        assert not np.isnan(T_interpolado).any(), "Interpolación generó NaN"
        assert not np.isinf(T_interpolado).any(), "Interpolación generó Inf"
        
        return T_interpolado


def actualizar_placa(T_placa_old: np.ndarray,
                     T_fluido: np.ndarray,
                     params: Parametros,
                     mallas: Dict,
                     dt: float) -> np.ndarray:
    """
    Actualiza la temperatura de la placa usando FTCS 2D con BCs Robin.
    
    Implementa las ecuaciones del documento:
    - Ecuación 11 (placa): FTCS 2D para nodos internos
    - Ecuación 12: BC Robin en interfaz agua (j=0)
    - Ecuación 13: BC Robin en superficie aire (j=Ny-1)
    
    Ecuación 11 (nodos internos):
        T_{i,j}^{n+1} = T_{i,j}^n + Fo_x(T_{i+1,j}^n - 2T_{i,j}^n + T_{i-1,j}^n)
                                   + Fo_y(T_{i,j+1}^n - 2T_{i,j}^n + T_{i,j-1}^n)
    
    Ecuación 12 (j=0, agua):
        T_{i,0}^{n+1} = T_{i,0}^n + Fo_x(T_{i+1,0}^n - 2T_{i,0}^n + T_{i-1,0}^n)
                                   + 2Fo_y[(T_{i,1}^n - T_{i,0}^n) - (h_agua·Δy/k_s)(T_{i,0}^n - T_{f,i}^n)]
    
    Ecuación 13 (j=Ny-1, aire):
        T_{i,Ny-1}^{n+1} = T_{i,Ny-1}^n + Fo_x(T_{i+1,Ny-1}^n - 2T_{i,Ny-1}^n + T_{i-1,Ny-1}^n)
                                         + 2Fo_y[(T_{i,Ny-2}^n - T_{i,Ny-1}^n) + (h_aire·Δy/k_s)(T_{i,Ny-1}^n - T_∞)]
    
    Args:
        T_placa_old (ndarray): Temperatura actual de la placa [K]
            Shape: (Nx_placa, Ny_placa)
        T_fluido (ndarray): Temperatura del fluido [K]
            Shape: (Nx_fluido,)
        params (Parametros): Objeto con parámetros del sistema
        mallas (dict): Diccionario con todas las mallas del sistema
        dt (float): Paso de tiempo [s]
    
    Returns:
        ndarray: Temperatura actualizada de la placa [K]
            Shape: (Nx_placa, Ny_placa)
    
    Raises:
        AssertionError: Si Fo_x + Fo_y ≥ 0.5 (inestabilidad numérica)
        AssertionError: Si se detectan NaN, Inf o temperaturas no físicas
    
    Notes:
        - Esquema FTCS: estable si Fo_x + Fo_y < 0.5
        - BCs Robin: convección en y=0 (agua) y y=e_base (aire)
        - BCs laterales (x=0, x=L_x): aislamiento (∂T/∂x = 0)
        - Fourier esperado (Al): ~0.27 < 0.5 ✓
    
    References:
        - Ecuaciones: contexto/05_discretizacion_numerica.md - Secciones 4.2, 4.3
        - Método FTCS: Hensen & Nakhi (1994)
    """
    # Extraer parámetros
    alpha = params.alpha_s
    k_s = params.k_s
    h_agua = params.h_agua
    h_aire = params.h_aire
    T_inf = params.T_inf
    Nx = params.Nx_placa
    Ny = params.Ny_placa
    dx = mallas['placa']['dx']
    dy = mallas['placa']['dy']
    x_placa = mallas['placa']['x']
    x_fluido = mallas['fluido']['x']
    
    # Validar entrada
    assert T_placa_old.shape == (Nx, Ny), \
        f"Shape de T_placa_old incorrecto: {T_placa_old.shape} != ({Nx}, {Ny})"
    assert not np.isnan(T_placa_old).any(), "T_placa_old contiene NaN"
    assert not np.isinf(T_placa_old).any(), "T_placa_old contiene Inf"
    
    # Calcular números de Fourier
    Fo_x = alpha * dt / (dx ** 2)
    Fo_y = alpha * dt / (dy ** 2)
    Fo_total = Fo_x + Fo_y
    
    # Validar estabilidad (criterio de Fourier)
    assert Fo_total < 0.5, \
        f"INESTABILIDAD: Fo_x + Fo_y = {Fo_total:.4f} ≥ 0.5. Reducir dt."
    
    # Interpolar temperatura del fluido si es necesario
    T_f_interpolado = _interpolar_fluido_a_placa(T_fluido, x_fluido, x_placa)
    
    # Validar temperatura del fluido
    assert not np.isnan(T_f_interpolado).any(), "T_fluido contiene NaN"
    assert not np.isinf(T_f_interpolado).any(), "T_fluido contiene Inf"
    
    # Crear array para temperatura nueva
    T_placa_new = np.zeros_like(T_placa_old)
    
    # ========== ECUACIÓN 11: NODOS INTERNOS (FTCS 2D) ==========
    # Para i = 1 hasta Nx-2, j = 1 hasta Ny-2
    
    i_inner = slice(1, Nx-1)
    j_inner = slice(1, Ny-1)
    
    T_placa_new[i_inner, j_inner] = (
        T_placa_old[i_inner, j_inner]
        + Fo_x * (T_placa_old[2:, j_inner] - 2*T_placa_old[i_inner, j_inner] + T_placa_old[:-2, j_inner])
        + Fo_y * (T_placa_old[i_inner, 2:] - 2*T_placa_old[i_inner, j_inner] + T_placa_old[i_inner, :-2])
    )
    
    # ========== ECUACIÓN 12: BC ROBIN EN AGUA (j=0) ==========
    # Interfaz con agua en y=0
    # T_{i,0}^{n+1} = T_{i,0}^n + Fo_x(...) + 2Fo_y[(T_{i,1}^n - T_{i,0}^n) - (h_agua·Δy/k_s)(T_{i,0}^n - T_f_i^n)]
    
    j = 0  # Superficie inferior (agua)
    coef_agua = h_agua * dy / k_s
    
    # Para nodos internos en x
    i_inner = slice(1, Nx-1)
    T_placa_new[i_inner, j] = (
        T_placa_old[i_inner, j]
        + Fo_x * (T_placa_old[2:, j] - 2*T_placa_old[i_inner, j] + T_placa_old[:-2, j])
        + 2*Fo_y * ((T_placa_old[i_inner, 1] - T_placa_old[i_inner, j])
                    - coef_agua * (T_placa_old[i_inner, j] - T_f_interpolado[i_inner]))
    )
    
    # ========== ECUACIÓN 13: BC ROBIN EN AIRE (j=Ny-1) ==========
    # Superficie superior en y=e_base
    # CORRECCIÓN: El signo del término convectivo debe permitir calentamiento cuando T_∞ > T_s
    # T_{i,Ny-1}^{n+1} = T_{i,Ny-1}^n + Fo_x(...) + 2Fo_y[(T_{i,Ny-2}^n - T_{i,Ny-1}^n) - (h_aire·Δy/k_s)(T_{i,Ny-1}^n - T_∞)]
    
    j = Ny - 1  # Superficie superior (aire)
    coef_aire = h_aire * dy / k_s
    
    # Para nodos internos en x
    i_inner = slice(1, Nx-1)
    T_placa_new[i_inner, j] = (
        T_placa_old[i_inner, j]
        + Fo_x * (T_placa_old[2:, j] - 2*T_placa_old[i_inner, j] + T_placa_old[:-2, j])
        + 2*Fo_y * ((T_placa_old[i_inner, Ny-2] - T_placa_old[i_inner, j])
                    - coef_aire * (T_placa_old[i_inner, j] - T_inf))
    )
    
    # ========== CONDICIONES DE FRONTERA LATERALES (x=0, x=L_x) ==========
    # Opción 1: Aislamiento (∂T/∂x = 0) - Extrapolación
    # Opción 2: Simetría - Copiar del vecino
    # Usaré extrapolación de orden 0 (más simple y estable)
    
    # Borde izquierdo (i=0)
    T_placa_new[0, :] = T_placa_new[1, :]
    
    # Borde derecho (i=Nx-1)
    T_placa_new[Nx-1, :] = T_placa_new[Nx-2, :]
    
    # ========== ESQUINAS (4 esquinas) ==========
    # Las esquinas ya quedan definidas por las BCs laterales
    # que copian de sus vecinos
    
    # ========== VALIDACIONES DE SALIDA ==========
    
    assert not np.isnan(T_placa_new).any(), \
        "ERROR: Actualización generó NaN"
    assert not np.isinf(T_placa_new).any(), \
        "ERROR: Actualización generó Inf"
    
    # Verificar rango físico
    T_min, T_max = T_placa_new.min(), T_placa_new.max()
    assert 200 < T_min < 400, \
        f"Temperatura mínima fuera de rango físico: {T_min:.2f} K"
    assert 200 < T_max < 400, \
        f"Temperatura máxima fuera de rango físico: {T_max:.2f} K"
    
    return T_placa_new


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Agregar el directorio raíz al path para imports absolutos
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.parametros import Parametros
    from src.mallas import generar_todas_mallas
    
    print("=" * 70)
    print("SOLVER DE LA PLACA - Sistema de Enfriamiento GPU")
    print("=" * 70)
    
    # Crear parámetros y mallas
    print("\n📐 Inicializando sistema...")
    params = Parametros('Al')
    mallas = generar_todas_mallas(params)
    
    # Inicializar temperatura de la placa
    print("\n🌡️  Inicializando campo de temperatura de la placa...")
    T_placa = inicializar_placa(params, mallas)
    
    print(f"  ✅ Campo inicializado: {T_placa.shape} = {T_placa.size} nodos")
    print(f"  Temperatura inicial uniforme: {T_placa[0, 0] - 273.15:.1f}°C")
    print(f"  Rango: [{T_placa.min() - 273.15:.1f}, {T_placa.max() - 273.15:.1f}]°C")
    
    # Inicializar fluido para acoplamiento
    # NOTA: Para testing, simulamos fluido a T_f_in = 80°C constante
    # representando agua caliente que entra al sistema
    print("\n🌊 Simulando fluido a temperatura de entrada (80°C)...")
    T_fluido = np.full(params.Nx_fluido, params.T_f_in, dtype=np.float64)
    print(f"  Temperatura del fluido (simulada): {params.T_f_in - 273.15:.1f}°C")
    print(f"  (En simulación real, el fluido se actualizaría con su propio solver)")
    print(f"  Placa inicial: {params.T_inicial - 273.15:.1f}°C → Será calentada por el agua")
    
    # Paso de tiempo
    dt = params.dt
    
    # Calcular números de Fourier
    Fo_x = params.Fo_x
    Fo_y = params.Fo_y
    Fo_total = Fo_x + Fo_y
    
    print(f"\n🧪 Parámetros de simulación:")
    print(f"  - dt: {dt:.2e} s")
    print(f"  - Fo_x: {Fo_x:.4f}")
    print(f"  - Fo_y: {Fo_y:.4f}")
    print(f"  - Fo_total: {Fo_total:.4f} (debe ser < 0.5)")
    print(f"  - α (Al): {params.alpha_s:.2e} m²/s")
    
    # Realizar varias actualizaciones
    # Tiempo característico de difusión: τ = L²/α = (0.01)²/(6.87e-5) ≈ 1.45 s
    # Simulamos ~20× ese tiempo para alcanzar estado cercano al estacionario
    num_pasos = 40000  # 40000 pasos × 0.5 ms = 20 segundos de simulación
    print(f"\n⏱️  Ejecutando {num_pasos} pasos de tiempo (t_final = {num_pasos * dt:.1f} s)...")
    print(f"  Tiempo característico difusión τ = L²/α ≈ 1.45 s")
    for n in range(num_pasos):
        T_placa = actualizar_placa(T_placa, T_fluido, params, mallas, dt)
        # Mostrar progreso en intervalos logarítmicos
        if n in [0, 99, 999, 2999, 5999, 9999, 19999, 29999, 39999]:
            t_actual = (n + 1) * dt
            T_min = T_placa.min() - 273.15
            T_max = T_placa.max() - 273.15
            T_centro = T_placa[params.Nx_placa//2, params.Ny_placa//2] - 273.15
            T_sup_agua = T_placa[:, 0].mean() - 273.15
            T_sup_aire = T_placa[:, -1].mean() - 273.15
            print(f"    t = {t_actual:.2e} s | T_min = {T_min:.2f}°C | "
                  f"T_max = {T_max:.2f}°C | T_centro = {T_centro:.2f}°C")
            print(f"      T_agua(promedio) = {T_sup_agua:.2f}°C | "
                  f"T_aire(promedio) = {T_sup_aire:.2f}°C")
    
    print("\n" + "=" * 70)
    print("✅ Solver de la placa funcionando correctamente")
    print("=" * 70)
    
    # Información adicional
    print("\n📊 Estadísticas finales:")
    print(f"  Temperatura mínima: {T_placa.min() - 273.15:.2f}°C")
    print(f"  Temperatura máxima: {T_placa.max() - 273.15:.2f}°C")
    print(f"  Temperatura promedio: {T_placa.mean() - 273.15:.2f}°C")
    print(f"  Temperatura en centro: {T_placa[params.Nx_placa//2, params.Ny_placa//2] - 273.15:.2f}°C")
    print(f"  Temperatura superficie agua: {T_placa[:, 0].mean() - 273.15:.2f}°C")
    print(f"  Temperatura superficie aire: {T_placa[:, -1].mean() - 273.15:.2f}°C")

