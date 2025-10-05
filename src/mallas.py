"""
Módulo de generación de mallas para el sistema de enfriamiento GPU.

Este módulo contiene funciones para generar las mallas de discretización espacial
para los tres dominios del problema:
- Fluido: Malla 1D en dirección x
- Placa: Malla 2D cartesiana en plano x-y
- Aletas: Mallas 2D cilíndricas en plano r-θ (3 aletas)

Referencias:
- Discretización: contexto/05_discretizacion_numerica.md - Sección 2
- Parámetros: contexto/02_parametros_sistema.md
"""

import numpy as np
from typing import Dict, List, Tuple
from .parametros import Parametros


def generar_malla_fluido(params: Parametros) -> Dict:
    """
    Genera la malla 1D para el dominio del fluido.
    
    El fluido fluye en dirección x desde x=0 (entrada) hasta x=L_x (salida).
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
    
    Returns:
        dict: Diccionario con la malla del fluido
            - 'x' (ndarray): Coordenadas de los nodos [m]
            - 'dx' (float): Espaciamiento entre nodos [m]
            - 'Nx' (int): Número de nodos
    
    Notes:
        - Malla uniforme con Nx=60 nodos
        - Extensión: 0 ≤ x ≤ 0.03 m
        - Δx ≈ 5.08×10⁻⁴ m = 0.508 mm
        - i=0: entrada (x=0), i=59: salida (x=L_x)
    
    References:
        Ver contexto/05_discretizacion_numerica.md - Sección 2
    """
    # Extraer parámetros
    L_x = params.L_x
    Nx = params.Nx_fluido
    dx = params.dx_fluido
    
    # Generar coordenadas usando linspace (incluye ambos extremos)
    x = np.linspace(0.0, L_x, Nx)
    
    # Validaciones
    assert len(x) == Nx, f"Tamaño de malla inconsistente: {len(x)} != {Nx}"
    assert np.isclose(x[1] - x[0], dx, rtol=1e-6), \
        f"Espaciamiento inconsistente: {x[1]-x[0]:.6e} != {dx:.6e}"
    assert x[0] == 0.0, "La malla debe empezar en x=0"
    assert np.isclose(x[-1], L_x, rtol=1e-6), \
        f"La malla debe terminar en x=L_x: {x[-1]:.6e} != {L_x:.6e}"
    
    return {
        'x': x,
        'dx': dx,
        'Nx': Nx
    }


def generar_malla_placa(params: Parametros) -> Dict:
    """
    Genera la malla 2D cartesiana para el dominio de la placa.
    
    La placa se discretiza en el plano x-y donde:
    - x: dirección del flujo (0 ≤ x ≤ L_x)
    - y: espesor de la placa (0 ≤ y ≤ e_base)
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
    
    Returns:
        dict: Diccionario con la malla de la placa
            - 'x' (ndarray): Coordenadas en x [m]
            - 'y' (ndarray): Coordenadas en y [m]
            - 'dx' (float): Espaciamiento en x [m]
            - 'dy' (float): Espaciamiento en y [m]
            - 'Nx' (int): Número de nodos en x
            - 'Ny' (int): Número de nodos en y
            - 'X' (ndarray): Meshgrid de coordenadas x (Nx, Ny)
            - 'Y' (ndarray): Meshgrid de coordenadas y (Nx, Ny)
    
    Notes:
        - Malla uniforme: 60×20 nodos
        - Extensión: [0, 0.03] × [0, 0.01] m
        - Δx ≈ 5.08×10⁻⁴ m, Δy ≈ 5.26×10⁻⁴ m
        - j=0: interfaz con agua (y=0)
        - j=19: superficie superior expuesta al aire (y=e_base)
    
    References:
        Ver contexto/05_discretizacion_numerica.md - Sección 2
    """
    # Extraer parámetros
    L_x = params.L_x
    e_base = params.e_base
    Nx = params.Nx_placa
    Ny = params.Ny_placa
    dx = params.dx_placa
    dy = params.dy_placa
    
    # Generar coordenadas 1D
    x = np.linspace(0.0, L_x, Nx)
    y = np.linspace(0.0, e_base, Ny)
    
    # Crear meshgrid para cálculos vectorizados
    # indexing='ij' para que X[i,j] corresponda a x[i], Y[i,j] corresponda a y[j]
    X, Y = np.meshgrid(x, y, indexing='ij')
    
    # Validaciones
    assert len(x) == Nx, f"Tamaño en x inconsistente: {len(x)} != {Nx}"
    assert len(y) == Ny, f"Tamaño en y inconsistente: {len(y)} != {Ny}"
    assert np.isclose(x[1] - x[0], dx, rtol=1e-6), \
        f"Espaciamiento dx inconsistente: {x[1]-x[0]:.6e} != {dx:.6e}"
    assert np.isclose(y[1] - y[0], dy, rtol=1e-6), \
        f"Espaciamiento dy inconsistente: {y[1]-y[0]:.6e} != {dy:.6e}"
    assert X.shape == (Nx, Ny), f"Shape de X incorrecto: {X.shape} != ({Nx}, {Ny})"
    assert Y.shape == (Nx, Ny), f"Shape de Y incorrecto: {Y.shape} != ({Nx}, {Ny})"
    
    return {
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy,
        'Nx': Nx,
        'Ny': Ny,
        'X': X,
        'Y': Y
    }


def generar_mallas_aletas(params: Parametros) -> List[Dict]:
    """
    Genera las mallas 2D cilíndricas para las 3 aletas (domos).
    
    Cada aleta se discretiza en coordenadas cilíndricas (r, θ) donde:
    - r: dirección radial (0 ≤ r ≤ R = 0.004 m)
    - θ: dirección angular (0 ≤ θ ≤ π rad, semicircunferencia)
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
    
    Returns:
        list: Lista con 3 diccionarios, uno por cada aleta
            Cada diccionario contiene:
            - 'r' (ndarray): Coordenadas radiales [m]
            - 'theta' (ndarray): Coordenadas angulares [rad]
            - 'dr' (float): Espaciamiento radial [m]
            - 'dtheta' (float): Espaciamiento angular [rad]
            - 'Nr' (int): Número de nodos radiales
            - 'Ntheta' (int): Número de nodos angulares
            - 'R' (ndarray): Meshgrid de r (Nr, Ntheta)
            - 'THETA' (ndarray): Meshgrid de θ (Nr, Ntheta)
            - 'x_centro' (float): Posición del centro de la aleta en eje x [m]
            - 'k_aleta' (int): Índice de la aleta (0, 1, 2)
    
    Notes:
        - Malla uniforme: 10×20 nodos por aleta
        - Extensión: [0, 0.004] × [0, π] m×rad
        - Δr ≈ 4.44×10⁻⁴ m, Δθ ≈ 0.165 rad = 9.47°
        - j=0: centro (r=0, con tratamiento especial por singularidad)
        - j=9: superficie curva (r=R, convección con aire)
        - m=0 y m=19: bordes planos (interfaz con placa)
        
        Posiciones de centros de aletas:
        - Aleta 0 (k=0): x = 0.005 m
        - Aleta 1 (k=1): x = 0.015 m
        - Aleta 2 (k=2): x = 0.025 m
    
    References:
        Ver contexto/05_discretizacion_numerica.md - Sección 2
    """
    # Extraer parámetros
    R = params.r  # Radio de las aletas (= D/2 = 0.004 m)
    Nr = params.Nr_aleta
    Ntheta = params.Ntheta_aleta
    dr = params.dr_aleta
    dtheta = params.dtheta_aleta
    
    # Posiciones de los centros de las aletas en eje x
    x_centros = [params.x_aleta_1, params.x_aleta_2, params.x_aleta_3]
    
    # Generar coordenadas 1D (iguales para las 3 aletas)
    r = np.linspace(0.0, R, Nr)
    theta = np.linspace(0.0, np.pi, Ntheta)
    
    # Crear meshgrid
    R_mesh, THETA_mesh = np.meshgrid(r, theta, indexing='ij')
    
    # Validaciones comunes
    assert len(r) == Nr, f"Tamaño en r inconsistente: {len(r)} != {Nr}"
    assert len(theta) == Ntheta, f"Tamaño en θ inconsistente: {len(theta)} != {Ntheta}"
    assert np.isclose(r[1] - r[0], dr, rtol=1e-6), \
        f"Espaciamiento dr inconsistente: {r[1]-r[0]:.6e} != {dr:.6e}"
    assert np.isclose(theta[1] - theta[0], dtheta, rtol=1e-6), \
        f"Espaciamiento dθ inconsistente: {theta[1]-theta[0]:.6e} != {dtheta:.6e}"
    assert np.isclose(theta[-1], np.pi, rtol=1e-6), \
        f"La malla angular debe terminar en π: {theta[-1]:.6e} != {np.pi:.6e}"
    assert R_mesh.shape == (Nr, Ntheta), \
        f"Shape de R incorrecto: {R_mesh.shape} != ({Nr}, {Ntheta})"
    
    # Crear lista de mallas (una por aleta)
    mallas_aletas = []
    for k in range(3):
        malla_k = {
            'r': r.copy(),
            'theta': theta.copy(),
            'dr': dr,
            'dtheta': dtheta,
            'Nr': Nr,
            'Ntheta': Ntheta,
            'R': R_mesh.copy(),
            'THETA': THETA_mesh.copy(),
            'x_centro': x_centros[k],
            'k_aleta': k
        }
        mallas_aletas.append(malla_k)
    
    return mallas_aletas


def generar_todas_mallas(params: Parametros) -> Dict:
    """
    Genera todas las mallas del sistema de enfriamiento y las retorna
    en un diccionario estructurado.
    
    Esta es la función maestra que llama a las funciones individuales
    y organiza todas las mallas en una estructura única.
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
    
    Returns:
        dict: Diccionario con todas las mallas del sistema
            - 'fluido': dict con malla 1D del fluido
            - 'placa': dict con malla 2D cartesiana de la placa
            - 'aletas': list con 3 dicts de mallas 2D cilíndricas
            - 'total_nodos': int con el número total de nodos en el sistema
    
    Notes:
        Total de nodos en el sistema:
        - Fluido: 60
        - Placa: 60 × 20 = 1,200
        - Aletas: 3 × (10 × 20) = 600
        - TOTAL: 1,860 nodos
    
    Examples:
        >>> from src.parametros import Parametros
        >>> params = Parametros('Al')
        >>> mallas = generar_todas_mallas(params)
        >>> print(f"Total de nodos: {mallas['total_nodos']}")
        Total de nodos: 1860
        >>> print(f"Malla fluido: {mallas['fluido']['Nx']} nodos")
        Malla fluido: 60 nodos
    """
    # Generar cada malla
    malla_fluido = generar_malla_fluido(params)
    malla_placa = generar_malla_placa(params)
    mallas_aletas = generar_mallas_aletas(params)
    
    # Calcular total de nodos
    n_fluido = malla_fluido['Nx']
    n_placa = malla_placa['Nx'] * malla_placa['Ny']
    n_aletas = sum(m['Nr'] * m['Ntheta'] for m in mallas_aletas)
    total_nodos = n_fluido + n_placa + n_aletas
    
    # Validar total esperado
    assert total_nodos == 1860, \
        f"Total de nodos incorrecto: {total_nodos} != 1860 esperados"
    
    # Construir diccionario completo
    mallas = {
        'fluido': malla_fluido,
        'placa': malla_placa,
        'aletas': mallas_aletas,
        'total_nodos': total_nodos
    }
    
    return mallas


def visualizar_mallas(mallas: Dict, params: Parametros) -> None:
    """
    Función opcional para visualizar las mallas generadas.
    
    Crea una figura con 4 subplots mostrando:
    1. Malla 1D del fluido
    2. Malla 2D de la placa (vista x-y)
    3. Mallas 2D de las aletas (coordenadas polares)
    4. Vista integrada del sistema completo
    
    Args:
        mallas (dict): Diccionario con todas las mallas generadas
        params (Parametros): Objeto con parámetros del sistema
    
    Notes:
        Esta función requiere matplotlib. Si no está disponible,
        se muestra un mensaje informativo sin generar error.
        
        La visualización ayuda a verificar que las mallas están
        correctamente generadas antes de proceder con la simulación.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib no disponible. Saltando visualización.")
        return
    
    fig = plt.figure(figsize=(14, 10))
    
    # 1. Malla del fluido
    ax1 = plt.subplot(2, 2, 1)
    x_f = mallas['fluido']['x']
    ax1.plot(x_f * 1e3, np.zeros_like(x_f), 'bo-', markersize=3)
    ax1.set_xlabel('x [mm]')
    ax1.set_title(f'Malla 1D del Fluido ({mallas["fluido"]["Nx"]} nodos)')
    ax1.set_ylim(-0.1, 0.1)
    ax1.grid(True, alpha=0.3)
    
    # 2. Malla de la placa
    ax2 = plt.subplot(2, 2, 2)
    X = mallas['placa']['X']
    Y = mallas['placa']['Y']
    ax2.plot(X * 1e3, Y * 1e3, 'b.', markersize=1, alpha=0.5)
    ax2.plot(X.T * 1e3, Y.T * 1e3, 'b.', markersize=1, alpha=0.5)
    ax2.set_xlabel('x [mm]')
    ax2.set_ylabel('y [mm]')
    ax2.set_title(f'Malla 2D de la Placa ({mallas["placa"]["Nx"]}×{mallas["placa"]["Ny"]} nodos)')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    # 3. Mallas de las aletas (en coordenadas polares)
    ax3 = plt.subplot(2, 2, 3, projection='polar')
    for k, malla_k in enumerate(mallas['aletas']):
        R = malla_k['R']
        THETA = malla_k['THETA']
        ax3.plot(THETA, R * 1e3, 'o', markersize=2, alpha=0.6, label=f'Aleta {k+1}')
    ax3.set_title(f'Mallas de las Aletas (×3, {mallas["aletas"][0]["Nr"]}×{mallas["aletas"][0]["Ntheta"]} c/u)')
    ax3.set_theta_zero_location('E')
    ax3.set_theta_direction(1)
    ax3.set_ylim(0, params.r * 1e3)
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Vista integrada (esquemática)
    ax4 = plt.subplot(2, 2, 4)
    
    # Dibujar placa
    ax4.add_patch(plt.Rectangle((0, 0), params.L_x * 1e3, params.e_base * 1e3,
                                 facecolor='lightblue', edgecolor='blue', alpha=0.3))
    ax4.text(params.L_x * 1e3 / 2, params.e_base * 1e3 / 2, 'PLACA',
             ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Dibujar aletas (semicírculos)
    for k, malla_k in enumerate(mallas['aletas']):
        x_c = malla_k['x_centro'] * 1e3
        circle = plt.Circle((x_c, params.e_base * 1e3), params.r * 1e3,
                           facecolor='lightcoral', edgecolor='red', alpha=0.5)
        ax4.add_patch(circle)
        ax4.text(x_c, params.e_base * 1e3 + params.r * 1e3, f'A{k+1}',
                ha='center', va='bottom', fontsize=8)
    
    # Dibujar canal de fluido
    ax4.add_patch(plt.Rectangle((0, -params.e_agua * 1e3), params.L_x * 1e3, params.e_agua * 1e3,
                                 facecolor='lightgreen', edgecolor='green', alpha=0.3))
    ax4.text(params.L_x * 1e3 / 2, -params.e_agua * 1e3 / 2, 'FLUIDO',
             ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax4.set_xlabel('x [mm]')
    ax4.set_ylabel('y [mm]')
    ax4.set_title('Vista Integrada del Sistema')
    ax4.set_aspect('equal')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(-2, params.L_x * 1e3 + 2)
    ax4.set_ylim(-params.e_agua * 1e3 - 1, params.e_base * 1e3 + params.r * 1e3 + 1)
    
    plt.tight_layout()
    plt.savefig('resultados/figuras/mallas_sistema.png', dpi=150, bbox_inches='tight')
    print("\n💾 Figura guardada en: resultados/figuras/mallas_sistema.png")
    plt.show()


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from parametros import Parametros
    
    print("=" * 70)
    print("GENERACIÓN DE MALLAS - Sistema de Enfriamiento GPU")
    print("=" * 70)
    
    # Crear parámetros con Aluminio
    params = Parametros('Al')
    
    # Generar todas las mallas
    print("\n📐 Generando mallas...")
    mallas = generar_todas_mallas(params)
    
    # Mostrar información
    print("\n✅ Mallas generadas exitosamente\n")
    
    print("MALLA DEL FLUIDO (1D)")
    print("-" * 70)
    print(f"  Número de nodos: {mallas['fluido']['Nx']}")
    print(f"  Extensión x: [{mallas['fluido']['x'][0]:.6f}, "
          f"{mallas['fluido']['x'][-1]:.6f}] m")
    print(f"  Espaciamiento dx: {mallas['fluido']['dx']:.6e} m = "
          f"{mallas['fluido']['dx']*1e3:.3f} mm")
    
    print("\nMALLA DE LA PLACA (2D Cartesiano)")
    print("-" * 70)
    print(f"  Número de nodos: {mallas['placa']['Nx']} × {mallas['placa']['Ny']} "
          f"= {mallas['placa']['Nx'] * mallas['placa']['Ny']}")
    print(f"  Extensión x: [{mallas['placa']['x'][0]:.6f}, "
          f"{mallas['placa']['x'][-1]:.6f}] m")
    print(f"  Extensión y: [{mallas['placa']['y'][0]:.6f}, "
          f"{mallas['placa']['y'][-1]:.6f}] m")
    print(f"  Espaciamiento dx: {mallas['placa']['dx']:.6e} m = "
          f"{mallas['placa']['dx']*1e3:.3f} mm")
    print(f"  Espaciamiento dy: {mallas['placa']['dy']:.6e} m = "
          f"{mallas['placa']['dy']*1e3:.3f} mm")
    
    print("\nMALLAS DE LAS ALETAS (2D Cilíndrico, ×3)")
    print("-" * 70)
    for k, malla_k in enumerate(mallas['aletas']):
        print(f"  Aleta {k+1}:")
        print(f"    Centro en x: {malla_k['x_centro']:.3f} m")
        print(f"    Número de nodos: {malla_k['Nr']} × {malla_k['Ntheta']} "
              f"= {malla_k['Nr'] * malla_k['Ntheta']}")
        print(f"    Extensión r: [0, {malla_k['r'][-1]:.6f}] m")
        print(f"    Extensión θ: [0, {malla_k['theta'][-1]:.4f}] rad = [0, 180°]")
        print(f"    Espaciamiento dr: {malla_k['dr']:.6e} m = "
              f"{malla_k['dr']*1e3:.3f} mm")
        print(f"    Espaciamiento dθ: {malla_k['dtheta']:.4f} rad = "
              f"{np.degrees(malla_k['dtheta']):.2f}°")
    
    print("\nRESUMEN")
    print("-" * 70)
    print(f"  Total de nodos en el sistema: {mallas['total_nodos']}")
    print(f"    - Fluido: {mallas['fluido']['Nx']}")
    print(f"    - Placa: {mallas['placa']['Nx'] * mallas['placa']['Ny']}")
    print(f"    - Aletas (×3): {sum(m['Nr']*m['Ntheta'] for m in mallas['aletas'])}")
    
    print("\n" + "=" * 70)
    print("✅ Verificación completa: Todas las mallas son consistentes")
    print("=" * 70)
    
    # Intentar visualizar (opcional)
    print("\n📊 Generando visualización...")
    visualizar_mallas(mallas, params)

