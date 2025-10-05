"""
Módulo de solver del fluido para el sistema de enfriamiento GPU.

Este módulo implementa el solver 1D del fluido de refrigeración (agua)
usando el esquema Upwind para advección y Euler Explícito para el término temporal.

La ecuación implementada es:
    ∂T_f/∂t + u·∂T_f/∂x = -γ(T_f - T_s)

Donde:
- u: velocidad del fluido [m/s]
- γ: parámetro de acoplamiento térmico [s⁻¹]
- T_s: temperatura de la superficie de la placa en y=0

Referencias:
- Ecuación: contexto/03_ecuaciones_gobernantes.md - Ecuación 1
- Discretización: contexto/05_discretizacion_numerica.md - Sección 4.1
- Parámetros: contexto/02_parametros_sistema.md
"""

import numpy as np
from typing import Dict
from .parametros import Parametros


def inicializar_fluido(params: Parametros, mallas: Dict) -> np.ndarray:
    """
    Inicializa el campo de temperatura del fluido.
    
    El fluido parte con temperatura inicial uniforme excepto en la entrada
    donde se impone la temperatura de entrada.
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
        mallas (dict): Diccionario con todas las mallas del sistema
    
    Returns:
        ndarray: Array 1D con temperatura inicial del fluido [K]
            Shape: (Nx_fluido,)
    
    Notes:
        - Temperatura inicial: 23°C (296.15 K) excepto entrada
        - Entrada (i=0): 80°C (353.15 K) - Nueva temperatura de entrada
        - Rango físico esperado: [296, 354] K
    
    References:
        Ver contexto/02_parametros_sistema.md - Tabla II
    """
    # Extraer parámetros
    Nx = params.Nx_fluido
    T_inicial = params.T_inicial      # 296.15 K (23°C)
    T_entrada = params.T_f_in          # 353.15 K (80°C)
    
    # Crear array con temperatura inicial uniforme
    T_fluido = np.full(Nx, T_inicial, dtype=np.float64)
    
    # Aplicar condición de entrada (Dirichlet)
    T_fluido[0] = T_entrada
    
    # Validaciones
    assert T_fluido.shape == (Nx,), \
        f"Shape incorrecto: {T_fluido.shape} != ({Nx},)"
    assert not np.isnan(T_fluido).any(), "Inicialización contiene NaN"
    assert not np.isinf(T_fluido).any(), "Inicialización contiene Inf"
    assert 200 < T_fluido.min() < 400, \
        f"Temperatura inicial fuera de rango: {T_fluido.min():.2f} K"
    assert 200 < T_fluido.max() < 400, \
        f"Temperatura inicial fuera de rango: {T_fluido.max():.2f} K"
    
    return T_fluido


def _interpolar_superficie_placa(T_placa_superficie: np.ndarray, 
                                  x_placa: np.ndarray,
                                  x_fluido: np.ndarray) -> np.ndarray:
    """
    Interpola la temperatura de la superficie de la placa a los nodos del fluido.
    
    Esta función se usa cuando las mallas del fluido y la placa no coinciden
    exactamente en los nodos x.
    
    Args:
        T_placa_superficie (ndarray): Temperatura en superficie de la placa (y=0)
            Shape: (Nx_placa,)
        x_placa (ndarray): Coordenadas x de la malla de la placa [m]
            Shape: (Nx_placa,)
        x_fluido (ndarray): Coordenadas x de la malla del fluido [m]
            Shape: (Nx_fluido,)
    
    Returns:
        ndarray: Temperatura interpolada en nodos del fluido [K]
            Shape: (Nx_fluido,)
    
    Notes:
        Usa interpolación lineal (np.interp) que es rápida y suficiente
        dado que las mallas tienen resolución similar.
    """
    # Interpolación lineal
    T_interpolado = np.interp(x_fluido, x_placa, T_placa_superficie)
    
    # Validaciones
    assert T_interpolado.shape == x_fluido.shape, \
        f"Shape interpolación incorrecto: {T_interpolado.shape} != {x_fluido.shape}"
    assert not np.isnan(T_interpolado).any(), "Interpolación generó NaN"
    assert not np.isinf(T_interpolado).any(), "Interpolación generó Inf"
    
    return T_interpolado


def actualizar_fluido(T_fluido_old: np.ndarray,
                      T_superficie_placa: np.ndarray,
                      params: Parametros,
                      mallas: Dict,
                      dt: float) -> np.ndarray:
    """
    Actualiza la temperatura del fluido usando Upwind + Euler Explícito.
    
    Implementa la Ecuación 11 del documento:
        T_{f,i}^{n+1} = T_{f,i}^n - CFL(T_{f,i}^n - T_{f,i-1}^n) 
                        - γΔt(T_{f,i}^n - T_{s,i}^n)
    
    Donde:
    - CFL = u·Δt/Δx (debe ser < 1 para estabilidad)
    - γ = h_agua/(ρ_agua·c_p,agua·e_agua) [s⁻¹]
    - T_s = temperatura de la superficie de la placa
    
    Args:
        T_fluido_old (ndarray): Temperatura actual del fluido [K]
            Shape: (Nx_fluido,)
        T_superficie_placa (ndarray): Temperatura superficie de la placa en y=0 [K]
            Shape: (Nx_placa,) - se interpolará si no coincide con Nx_fluido
        params (Parametros): Objeto con parámetros del sistema
        mallas (dict): Diccionario con todas las mallas del sistema
        dt (float): Paso de tiempo [s]
    
    Returns:
        ndarray: Temperatura actualizada del fluido [K]
            Shape: (Nx_fluido,)
    
    Raises:
        AssertionError: Si CFL ≥ 1 (inestabilidad numérica)
        AssertionError: Si se detectan NaN, Inf o temperaturas no físicas
    
    Notes:
        - Esquema Upwind hacia atrás (i-1) porque u > 0
        - BC entrada (i=0): Dirichlet (T = T_f_in)
        - BC salida (i=Nx-1): Neumann (∂T/∂x = 0, extrapolación)
        - CFL esperado: ~0.109 < 1.0 ✓
    
    References:
        - Ecuación: contexto/05_discretizacion_numerica.md - Sección 4.1
        - Método Upwind: Shu & LeVeque (1991)
    """
    # Extraer parámetros necesarios
    u = params.u                       # Velocidad [m/s]
    gamma = params.gamma               # Parámetro de acoplamiento [s⁻¹]
    Nx = params.Nx_fluido
    dx = mallas['fluido']['dx']        # Espaciamiento [m]
    x_fluido = mallas['fluido']['x']   # Coordenadas x del fluido
    T_entrada = params.T_f_in          # Temperatura de entrada [K]
    
    # Validar entrada
    assert T_fluido_old.shape == (Nx,), \
        f"Shape de T_fluido_old incorrecto: {T_fluido_old.shape} != ({Nx},)"
    assert not np.isnan(T_fluido_old).any(), "T_fluido_old contiene NaN"
    assert not np.isinf(T_fluido_old).any(), "T_fluido_old contiene Inf"
    
    # Calcular número de Courant-Friedrichs-Lewy (CFL)
    CFL = u * dt / dx
    
    # Validar estabilidad (criterio CFL)
    assert CFL < 1.0, \
        f"INESTABILIDAD: CFL = {CFL:.4f} ≥ 1.0. Reducir dt o aumentar dx."
    
    # Interpolar T_superficie si las mallas no coinciden
    if len(T_superficie_placa) != Nx:
        x_placa = mallas['placa']['x']
        T_s = _interpolar_superficie_placa(T_superficie_placa, x_placa, x_fluido)
    else:
        T_s = T_superficie_placa
    
    # Validar temperatura de superficie
    assert T_s.shape == (Nx,), f"Shape de T_s incorrecto: {T_s.shape} != ({Nx},)"
    assert not np.isnan(T_s).any(), "T_superficie contiene NaN"
    assert not np.isinf(T_s).any(), "T_superficie contiene Inf"
    
    # Crear array para temperatura nueva
    T_fluido_new = np.zeros_like(T_fluido_old)
    
    # ========== ECUACIÓN 11: UPWIND + EULER EXPLÍCITO ==========
    
    # Nodos internos (i = 1 hasta Nx-2) - Vectorizado
    i = slice(1, Nx-1)
    T_fluido_new[i] = (T_fluido_old[i] 
                       - CFL * (T_fluido_old[i] - T_fluido_old[:-2])  # Término upwind
                       - gamma * dt * (T_fluido_old[i] - T_s[i]))      # Acoplamiento
    
    # ========== CONDICIONES DE FRONTERA ==========
    
    # Entrada (i=0): Dirichlet - Temperatura fija
    T_fluido_new[0] = T_entrada
    
    # Salida (i=Nx-1): Neumann - Derivada cero (extrapolación)
    T_fluido_new[-1] = T_fluido_new[-2]
    
    # ========== VALIDACIONES DE SALIDA ==========
    
    assert not np.isnan(T_fluido_new).any(), \
        "ERROR: Actualización generó NaN"
    assert not np.isinf(T_fluido_new).any(), \
        "ERROR: Actualización generó Inf"
    
    # Verificar rango físico
    T_min, T_max = T_fluido_new.min(), T_fluido_new.max()
    assert 200 < T_min < 400, \
        f"Temperatura mínima fuera de rango físico: {T_min:.2f} K"
    assert 200 < T_max < 400, \
        f"Temperatura máxima fuera de rango físico: {T_max:.2f} K"
    
    return T_fluido_new


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Agregar el directorio raíz al path para imports absolutos
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.parametros import Parametros
    from src.mallas import generar_todas_mallas
    
    print("=" * 70)
    print("SOLVER DEL FLUIDO - Sistema de Enfriamiento GPU")
    print("=" * 70)
    
    # Crear parámetros y mallas
    print("\n📐 Inicializando sistema...")
    params = Parametros('Al')
    mallas = generar_todas_mallas(params)
    
    # Inicializar temperatura del fluido
    print("\n🌡️  Inicializando campo de temperatura del fluido...")
    T_fluido = inicializar_fluido(params, mallas)
    
    print(f"  ✅ Campo inicializado: {len(T_fluido)} nodos")
    print(f"  Temperatura entrada (i=0): {T_fluido[0] - 273.15:.1f}°C")
    print(f"  Temperatura inicial (resto): {T_fluido[1] - 273.15:.1f}°C")
    print(f"  Rango: [{T_fluido.min() - 273.15:.1f}, {T_fluido.max() - 273.15:.1f}]°C")
    
    # Simular temperatura de superficie de placa (por ahora uniforme a T_inicial)
    print("\n🧪 Simulando actualización temporal...")
    T_placa_superficie = np.full(params.Nx_placa, params.T_inicial)
    
    # Paso de tiempo
    dt = params.dt
    
    # Calcular CFL
    CFL = params.u * dt / mallas['fluido']['dx']
    print(f"  Parámetros:")
    print(f"    - dt: {dt:.2e} s")
    print(f"    - CFL: {CFL:.4f} (debe ser < 1.0)")
    print(f"    - γ: {params.gamma:.4e} s⁻¹")
    
    # Realizar varias actualizaciones
    print("\n⏱️  Ejecutando 10 pasos de tiempo...")
    for n in range(10):
        T_fluido = actualizar_fluido(T_fluido, T_placa_superficie, 
                                     params, mallas, dt)
        if n == 0 or n == 4 or n == 9:
            t_actual = (n + 1) * dt
            print(f"    t = {t_actual:.2e} s | "
                  f"T_min = {T_fluido.min() - 273.15:.2f}°C | "
                  f"T_max = {T_fluido.max() - 273.15:.2f}°C | "
                  f"T_salida = {T_fluido[-1] - 273.15:.2f}°C")
    
    print("\n" + "=" * 70)
    print("✅ Solver del fluido funcionando correctamente")
    print("=" * 70)
    
    # Información adicional
    print("\n📊 Estadísticas finales:")
    print(f"  Temperatura en entrada: {T_fluido[0] - 273.15:.2f}°C (fija)")
    print(f"  Temperatura en salida: {T_fluido[-1] - 273.15:.2f}°C")
    print(f"  Temperatura promedio: {T_fluido.mean() - 273.15:.2f}°C")
    print(f"  Gradiente T_salida - T_entrada: {(T_fluido[-1] - T_fluido[0]):.2f} K")

