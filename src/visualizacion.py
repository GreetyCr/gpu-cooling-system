#!/usr/bin/env python3
"""
Módulo de Visualización - Sistema de Enfriamiento GPU

Contiene funciones para generar gráficos, animaciones y reportes visuales
de los resultados de la simulación.

Funciones principales:
    - graficar_evolucion_temporal: Temperaturas vs tiempo
    - graficar_perfiles_espaciales: T vs x/y/r/θ
    - graficar_campo_2d: Heatmaps de temperatura
    - crear_animacion: Animación de evolución térmica
    - comparar_materiales: Comparación Al vs SS
    - graficar_balance_energetico: Validación energética
    - graficar_convergencia: max|dT/dt| vs tiempo
    - generar_reporte_completo: Suite completa de visualizaciones

Autor: Sistema de Simulación
Fecha: Octubre 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import warnings

# Configuración de matplotlib para mejor calidad
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Directorio para guardar figuras
DIR_FIGURAS = Path(__file__).parent.parent / "resultados" / "figuras"
DIR_FIGURAS.mkdir(parents=True, exist_ok=True)


# =============================================================================
# FUNCIÓN 1: EVOLUCIÓN TEMPORAL
# =============================================================================

def graficar_evolucion_temporal(
    resultados: Dict,
    params: 'Parametros',
    titulo: str = "Evolución Térmica del Sistema",
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica la evolución temporal de temperaturas promedio en todos los dominios.
    
    Args:
        resultados (Dict): Diccionario con resultados de la simulación
            - 'tiempo': array de tiempos [s]
            - 'T_fluido': lista de arrays de temperatura del fluido [K]
            - 'T_placa': lista de arrays 2D de temperatura de la placa [K]
            - 'T_aletas': lista de [3 aletas] en cada tiempo [K]
        params (Parametros): Objeto con parámetros del sistema
        titulo (str): Título principal del gráfico
        guardar (bool): Si guardar la figura a archivo
        nombre_archivo (str): Nombre del archivo (default: auto)
        mostrar (bool): Si mostrar la figura interactivamente
    
    Returns:
        plt.Figure: Objeto de figura de matplotlib
    
    Examples:
        >>> fig = graficar_evolucion_temporal(resultados, params)
        >>> fig = graficar_evolucion_temporal(resultados, params, mostrar=True)
    """
    # Validaciones
    assert 'tiempo' in resultados, "Resultados debe contener 'tiempo'"
    assert 'T_fluido' in resultados, "Resultados debe contener 'T_fluido'"
    assert 'T_placa' in resultados, "Resultados debe contener 'T_placa'"
    assert 'T_aletas' in resultados, "Resultados debe contener 'T_aletas'"
    
    tiempo = resultados['tiempo']
    T_fluido = resultados['T_fluido']
    T_placa = resultados['T_placa']
    T_aletas = resultados['T_aletas']
    
    assert len(tiempo) > 0, "Debe haber al menos un punto temporal"
    assert len(tiempo) == len(T_fluido), "Longitudes inconsistentes"
    
    # Calcular temperaturas promedio
    T_f_mean = np.array([T.mean() - 273.15 for T in T_fluido])  # °C
    T_p_mean = np.array([T.mean() - 273.15 for T in T_placa])
    T_a_mean = np.array([np.mean([Ta.mean() for Ta in Tas]) - 273.15 
                         for Tas in T_aletas])
    
    # Crear figura
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Panel 1: Temperaturas promedio
    ax1.plot(tiempo, T_f_mean, 'b-', linewidth=2.5, label='Fluido', alpha=0.9)
    ax1.plot(tiempo, T_p_mean, 'r-', linewidth=2.5, label='Placa', alpha=0.9)
    ax1.plot(tiempo, T_a_mean, 'g-', linewidth=2.5, label='Aletas', alpha=0.9)
    
    ax1.axhline(params.T_inf - 273.15, color='gray', linestyle='--', 
                linewidth=1.5, alpha=0.7, label=f'T$_{{aire}}$ = {params.T_inf-273.15:.0f}°C')
    ax1.axhline(params.T_f_in - 273.15, color='cyan', linestyle='--', 
                linewidth=1.5, alpha=0.7, label=f'T$_{{entrada}}$ = {params.T_f_in-273.15:.0f}°C')
    
    ax1.set_xlabel('Tiempo (s)', fontweight='bold')
    ax1.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax1.set_title(titulo, fontsize=14, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(0, tiempo[-1])
    
    # Panel 2: Diferencias de temperatura
    dT_fp = T_f_mean - T_p_mean
    dT_pa = T_p_mean - T_a_mean
    
    ax2.plot(tiempo, dT_fp, 'purple', linewidth=2, label='ΔT Fluido-Placa', alpha=0.8)
    ax2.plot(tiempo, dT_pa, 'orange', linewidth=2, label='ΔT Placa-Aletas', alpha=0.8)
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    
    ax2.set_xlabel('Tiempo (s)', fontweight='bold')
    ax2.set_ylabel('Diferencia de Temperatura (°C)', fontweight='bold')
    ax2.set_title('Gradientes Térmicos entre Dominios', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(0, tiempo[-1])
    
    plt.tight_layout()
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"evolucion_temporal_{params.material}.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 2: PERFILES ESPACIALES
# =============================================================================

def graficar_perfiles_espaciales(
    resultados: Dict,
    mallas: Dict,
    params: 'Parametros',
    tiempo_idx: int = -1,
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica perfiles espaciales de temperatura en un instante dado.
    
    Args:
        resultados (Dict): Diccionario con resultados de la simulación
        mallas (Dict): Diccionario con todas las mallas del sistema
        params (Parametros): Objeto con parámetros del sistema
        tiempo_idx (int): Índice temporal a graficar (default: -1 = último)
        guardar (bool): Si guardar la figura
        nombre_archivo (str): Nombre del archivo (default: auto)
        mostrar (bool): Si mostrar la figura
    
    Returns:
        plt.Figure: Objeto de figura
    
    Notes:
        - Grafica 4 perfiles: fluido, placa (x e y), aleta (r y θ)
    """
    # Validaciones
    assert 'tiempo' in resultados, "Resultados debe contener 'tiempo'"
    assert tiempo_idx < len(resultados['tiempo']), "tiempo_idx fuera de rango"
    
    tiempo = resultados['tiempo'][tiempo_idx]
    T_f = resultados['T_fluido'][tiempo_idx] - 273.15  # °C
    T_p = resultados['T_placa'][tiempo_idx] - 273.15
    T_a0 = resultados['T_aletas'][tiempo_idx][0] - 273.15  # Primera aleta
    
    # Mallas (extraer coordenadas únicas)
    x_f = mallas['fluido']['x'] * 1000  # mm
    
    # Para placa: extraer coordenadas únicas si son meshgrid
    if mallas['placa']['x'].ndim == 2:
        x_p = mallas['placa']['x'][0, :] * 1000
        y_p = mallas['placa']['y'][:, 0] * 1000
    else:
        x_p = mallas['placa']['x'] * 1000
        y_p = mallas['placa']['y'] * 1000
    
    # Para aletas
    if mallas['aletas'][0]['r'].ndim == 2:
        r_a = mallas['aletas'][0]['r'][:, 0] * 1000
        theta_a = mallas['aletas'][0]['theta'][0, :] * 180 / np.pi
    else:
        r_a = mallas['aletas'][0]['r'] * 1000
        theta_a = mallas['aletas'][0]['theta'] * 180 / np.pi
    
    # Crear figura con GridSpec
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # Panel 1: Perfil del fluido (x)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(x_f, T_f, 'b-', linewidth=2.5, marker='o', markersize=3, alpha=0.8)
    ax1.set_xlabel('Posición x (mm)', fontweight='bold')
    ax1.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax1.set_title(f'Perfil de Temperatura del Fluido en t={tiempo:.2f}s', 
                  fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(params.T_inf - 273.15, color='gray', linestyle='--', 
                alpha=0.5, label='T_aire')
    ax1.legend()
    
    # Panel 2: Perfil de placa (dirección x, centro y)
    ax2 = fig.add_subplot(gs[1, 0])
    # T_p tiene forma (Nx, Ny), donde Nx es para x y Ny es para y
    idx_y_centro = T_p.shape[1] // 2  # Índice en dirección y
    T_p_x = T_p[:, idx_y_centro]  # Perfil en x, fijo y
    ax2.plot(x_p, T_p_x, 'r-', linewidth=2.5, marker='s', markersize=3, alpha=0.8)
    ax2.set_xlabel('Posición x (mm)', fontweight='bold')
    ax2.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax2.set_title(f'Perfil de Placa en dirección x (y={y_p[idx_y_centro]:.1f}mm)', 
                  fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Perfil de placa (dirección y, centro x)
    ax3 = fig.add_subplot(gs[1, 1])
    idx_x_centro = T_p.shape[0] // 2  # Índice en dirección x
    T_p_y = T_p[idx_x_centro, :]  # Perfil en y, fijo x
    ax3.plot(y_p, T_p_y, 'r-', linewidth=2.5, marker='s', markersize=3, alpha=0.8)
    ax3.set_xlabel('Posición y (mm)', fontweight='bold')
    ax3.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax3.set_title(f'Perfil de Placa en dirección y (x={x_p[idx_x_centro]:.1f}mm)', 
                  fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Panel 4: Perfil de aleta (dirección radial, θ=0)
    ax4 = fig.add_subplot(gs[2, 0])
    idx_theta_0 = 0
    # T_a0 tiene forma (Nr, Ntheta), donde Nr es radial y Ntheta es angular
    if T_a0.shape[0] == len(r_a):
        T_a_r = T_a0[:, idx_theta_0]
    else:
        T_a_r = T_a0[idx_theta_0, :]
        # Si las dimensiones están intercambiadas, usar theta_a como r
        if len(T_a_r) == len(theta_a):
            r_a, theta_a = theta_a, r_a  # Swap temporalmente
    
    ax4.plot(r_a, T_a_r, 'g-', linewidth=2.5, marker='^', markersize=3, alpha=0.8)
    ax4.set_xlabel('Radio r (mm)', fontweight='bold')
    ax4.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax4.set_title(f'Perfil Radial de Aleta (θ={theta_a[idx_theta_0] if idx_theta_0 < len(theta_a) else 0:.0f}°)', 
                  fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Panel 5: Perfil de aleta (dirección angular, r=R)
    ax5 = fig.add_subplot(gs[2, 1])
    idx_r_max = -1
    if T_a0.shape[1] == len(theta_a):
        T_a_theta = T_a0[idx_r_max, :]
    else:
        T_a_theta = T_a0[:, idx_r_max]
    
    ax5.plot(theta_a, T_a_theta, 'g-', linewidth=2.5, marker='^', markersize=3, alpha=0.8)
    ax5.set_xlabel('Ángulo θ (°)', fontweight='bold')
    ax5.set_ylabel('Temperatura (°C)', fontweight='bold')
    ax5.set_title(f'Perfil Angular de Aleta (r={r_a[idx_r_max]:.2f}mm)', 
                  fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # Título general
    fig.suptitle(f'Perfiles Espaciales de Temperatura - {params.material} - t={tiempo:.2f}s',
                 fontsize=14, fontweight='bold', y=0.995)
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"perfiles_espaciales_{params.material}_t{tiempo:.2f}s.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 3: CAMPOS 2D
# =============================================================================

def graficar_campo_2d(
    resultados: Dict,
    mallas: Dict,
    params: 'Parametros',
    tiempo_idx: int = -1,
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica campos 2D de temperatura (heatmaps) de placa y aletas.
    
    Args:
        resultados (Dict): Diccionario con resultados
        mallas (Dict): Diccionario con mallas
        params (Parametros): Parámetros del sistema
        tiempo_idx (int): Índice temporal (default: -1)
        guardar (bool): Si guardar
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar
    
    Returns:
        plt.Figure: Objeto de figura
    """
    # Validaciones
    assert tiempo_idx < len(resultados['tiempo']), "tiempo_idx fuera de rango"
    
    tiempo = resultados['tiempo'][tiempo_idx]
    T_p = np.asarray(resultados['T_placa'][tiempo_idx], dtype=float) - 273.15  # °C
    T_a = [np.asarray(T, dtype=float) - 273.15 for T in resultados['T_aletas'][tiempo_idx]]  # 3 aletas
    
    # Crear figura
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Panel 1: Campo de temperatura de la placa
    ax1 = fig.add_subplot(gs[0, :])
    
    # Manejar mallas 1D o 2D
    if mallas['placa']['x'].ndim == 2:
        x_p = mallas['placa']['x'] * 1000
        y_p = mallas['placa']['y'] * 1000
    else:
        # Crear meshgrid si son 1D
        x_p_1d = mallas['placa']['x'] * 1000
        y_p_1d = mallas['placa']['y'] * 1000
        x_p, y_p = np.meshgrid(x_p_1d, y_p_1d)
    
    im1 = ax1.contourf(x_p, y_p, T_p.T, levels=20, cmap='hot')
    cbar1 = plt.colorbar(im1, ax=ax1, label='Temperatura (°C)')
    ax1.set_xlabel('Posición x (mm)', fontweight='bold')
    ax1.set_ylabel('Posición y (mm)', fontweight='bold')
    ax1.set_title(f'Campo de Temperatura - Placa - t={tiempo:.2f}s', 
                  fontsize=12, fontweight='bold')
    ax1.set_aspect('equal')
    
    # Paneles 2-4: Campos de temperatura de las 3 aletas
    for k in range(3):
        ax = fig.add_subplot(gs[1, k], projection='polar')
        r_a = mallas['aletas'][k]['r']
        theta_a = mallas['aletas'][k]['theta']
        
        im = ax.contourf(theta_a, r_a * 1000, T_a[k], levels=15, cmap='hot')
        cbar = plt.colorbar(im, ax=ax, label='T (°C)', pad=0.1)
        ax.set_title(f'Aleta {k+1} - t={tiempo:.2f}s', fontsize=11, fontweight='bold')
        ax.set_theta_zero_location('E')
        ax.set_theta_direction(1)
    
    # Título general
    fig.suptitle(f'Campos de Temperatura 2D - {params.material}',
                 fontsize=14, fontweight='bold', y=0.995)
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"campos_2d_{params.material}_t{tiempo:.2f}s.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 4: BALANCE ENERGÉTICO
# =============================================================================

def graficar_balance_energetico(
    resultados: Dict,
    params: 'Parametros',
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica el balance energético del sistema (Q_in, Q_out, dE/dt).
    
    Args:
        resultados (Dict): Diccionario con resultados que incluye:
            - 'metricas': dict con 'balance' (lista de balances por tiempo)
        params (Parametros): Parámetros del sistema
        guardar (bool): Si guardar figura
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar
    
    Returns:
        plt.Figure: Objeto de figura
    
    Notes:
        - Requiere que se haya calculado el balance energético en la simulación
        - Muestra Q_in, Q_out, dE/dt y error relativo
    """
    # Validaciones
    assert 'metricas' in resultados, "Resultados debe contener 'metricas'"
    assert 'balance' in resultados['metricas'], "metricas debe contener 'balance'"
    assert len(resultados['metricas']['balance']) > 0, "balance no puede estar vacío"
    
    balance = resultados['metricas']['balance']
    
    # Extraer datos
    t_balance = np.array([b['tiempo'] for b in balance])
    Q_in = np.array([b['Q_in'] for b in balance])
    Q_out = np.array([b['Q_out'] for b in balance])
    dE_dt = np.array([b['dE_dt'] for b in balance])
    error_rel = np.array([b['error_relativo'] * 100 for b in balance])
    
    # Crear figura
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Panel 1: Potencias
    ax1.plot(t_balance, Q_in, 'b-', linewidth=2.5, label='Q$_{in}$ (entrada)', alpha=0.9)
    ax1.plot(t_balance, Q_out, 'r-', linewidth=2.5, label='Q$_{out}$ (salida)', alpha=0.9)
    ax1.plot(t_balance, dE_dt, 'g--', linewidth=2.5, label='dE/dt (acumulación)', alpha=0.9)
    ax1.set_xlabel('Tiempo (s)', fontweight='bold')
    ax1.set_ylabel('Potencia (W)', fontweight='bold')
    ax1.set_title('Balance de Potencia', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, t_balance[-1])
    
    # Panel 2: Diferencia Q_in - Q_out - dE/dt (debe ser ~ 0)
    balance_neto = Q_in - Q_out - dE_dt
    ax2.plot(t_balance, balance_neto, 'purple', linewidth=2, alpha=0.8)
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Tiempo (s)', fontweight='bold')
    ax2.set_ylabel('Q$_{in}$ - Q$_{out}$ - dE/dt (W)', fontweight='bold')
    ax2.set_title('Residuo del Balance (debe ser ≈ 0)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, t_balance[-1])
    
    # Panel 3: Error relativo
    ax3.plot(t_balance, error_rel, 'k-', linewidth=2, alpha=0.8)
    ax3.axhline(10, color='orange', linestyle='--', linewidth=1.5, 
                alpha=0.7, label='10% (aceptable)')
    ax3.axhline(40, color='red', linestyle='--', linewidth=1.5, 
                alpha=0.7, label='40% (límite)')
    ax3.set_xlabel('Tiempo (s)', fontweight='bold')
    ax3.set_ylabel('Error Relativo (%)', fontweight='bold')
    ax3.set_title('Error del Balance Energético', fontsize=12, fontweight='bold')
    ax3.legend(loc='best', framealpha=0.9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, t_balance[-1])
    ax3.set_ylim(0, max(50, error_rel.max()*1.1))
    
    # Título general
    fig.suptitle(f'Balance Energético del Sistema - {params.material}',
                 fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"balance_energetico_{params.material}.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 5: CONVERGENCIA
# =============================================================================

def graficar_convergencia(
    resultados: Dict,
    params: 'Parametros',
    epsilon: float = 1e-3,
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica la evolución de la tasa máxima de cambio de temperatura (convergencia).
    
    Args:
        resultados (Dict): Diccionario con resultados
        params (Parametros): Parámetros del sistema
        epsilon (float): Criterio de convergencia [K/s]
        guardar (bool): Si guardar
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar
    
    Returns:
        plt.Figure: Objeto de figura
    """
    # Calcular max|dT/dt| en cada punto temporal
    tiempo = resultados['tiempo']
    T_fluido = resultados['T_fluido']
    T_placa = resultados['T_placa']
    T_aletas = resultados['T_aletas']
    
    max_rates = []
    for i in range(1, len(tiempo)):
        dt = tiempo[i] - tiempo[i-1]
        
        # Calcular tasas de cambio
        dT_f = np.abs((T_fluido[i] - T_fluido[i-1]) / dt)
        dT_p = np.abs((T_placa[i] - T_placa[i-1]) / dt)
        dT_a = [np.abs((T_aletas[i][k] - T_aletas[i-1][k]) / dt) for k in range(3)]
        
        # Máximo global
        max_rate = max(dT_f.max(), dT_p.max(), max([dT.max() for dT in dT_a]))
        max_rates.append(max_rate)
    
    tiempo_plot = tiempo[1:]  # Excluir primer punto (no hay tasa)
    max_rates = np.array(max_rates)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.semilogy(tiempo_plot, max_rates, 'b-', linewidth=2.5, alpha=0.8, label='max|dT/dt|')
    ax.axhline(epsilon, color='red', linestyle='--', linewidth=2, 
               alpha=0.7, label=f'Criterio ε = {epsilon:.1e} K/s')
    
    # Marcar punto de convergencia si se alcanzó
    if 'convergencia' in resultados and resultados['convergencia']['alcanzada']:
        t_conv = resultados['convergencia']['t_convergencia']
        ax.axvline(t_conv, color='green', linestyle=':', linewidth=2, 
                   alpha=0.7, label=f'Convergencia en t={t_conv:.2f}s')
    
    ax.set_xlabel('Tiempo (s)', fontweight='bold')
    ax.set_ylabel('max|dT/dt| (K/s)', fontweight='bold')
    ax.set_title(f'Convergencia a Estado Estacionario - {params.material}', 
                 fontsize=12, fontweight='bold')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(0, tiempo_plot[-1])
    
    plt.tight_layout()
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"convergencia_{params.material}.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 6: COMPARACIÓN ENTRE MATERIALES
# =============================================================================

def comparar_materiales(
    resultados_al: Dict,
    resultados_ss: Dict,
    params_al: 'Parametros',
    params_ss: 'Parametros',
    guardar: bool = True,
    nombre_archivo: str = "comparacion_materiales.png",
    mostrar: bool = False
) -> plt.Figure:
    """
    Compara la evolución térmica de Aluminio vs Acero Inoxidable.
    
    Args:
        resultados_al (Dict): Resultados para Aluminio
        resultados_ss (Dict): Resultados para Acero Inoxidable
        params_al (Parametros): Parámetros de Aluminio
        params_ss (Parametros): Parámetros de Acero
        guardar (bool): Si guardar
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar
    
    Returns:
        plt.Figure: Objeto de figura
    """
    # Extraer datos Aluminio
    t_al = resultados_al['tiempo']
    T_f_al = np.array([T.mean() - 273.15 for T in resultados_al['T_fluido']])
    T_p_al = np.array([T.mean() - 273.15 for T in resultados_al['T_placa']])
    T_a_al = np.array([np.mean([Ta.mean() for Ta in Tas]) - 273.15 
                       for Tas in resultados_al['T_aletas']])
    
    # Extraer datos Acero
    t_ss = resultados_ss['tiempo']
    T_f_ss = np.array([T.mean() - 273.15 for T in resultados_ss['T_fluido']])
    T_p_ss = np.array([T.mean() - 273.15 for T in resultados_ss['T_placa']])
    T_a_ss = np.array([np.mean([Ta.mean() for Ta in Tas]) - 273.15 
                       for Tas in resultados_ss['T_aletas']])
    
    # Crear figura con 3 paneles
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
    
    # Panel 1: Fluido
    ax1.plot(t_al, T_f_al, 'b-', linewidth=2.5, label='Aluminio', alpha=0.9)
    ax1.plot(t_ss, T_f_ss, 'r--', linewidth=2.5, label='Acero Inox', alpha=0.9)
    ax1.set_xlabel('Tiempo (s)', fontweight='bold')
    ax1.set_ylabel('Temperatura Fluido (°C)', fontweight='bold')
    ax1.set_title('Comparación: Temperatura del Fluido', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Placa
    ax2.plot(t_al, T_p_al, 'b-', linewidth=2.5, label='Aluminio', alpha=0.9)
    ax2.plot(t_ss, T_p_ss, 'r--', linewidth=2.5, label='Acero Inox', alpha=0.9)
    ax2.set_xlabel('Tiempo (s)', fontweight='bold')
    ax2.set_ylabel('Temperatura Placa (°C)', fontweight='bold')
    ax2.set_title('Comparación: Temperatura de la Placa', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Aletas
    ax3.plot(t_al, T_a_al, 'b-', linewidth=2.5, label='Aluminio', alpha=0.9)
    ax3.plot(t_ss, T_a_ss, 'r--', linewidth=2.5, label='Acero Inox', alpha=0.9)
    ax3.set_xlabel('Tiempo (s)', fontweight='bold')
    ax3.set_ylabel('Temperatura Aletas (°C)', fontweight='bold')
    ax3.set_title('Comparación: Temperatura de las Aletas', fontsize=12, fontweight='bold')
    ax3.legend(loc='best', framealpha=0.9)
    ax3.grid(True, alpha=0.3)
    
    # Título general
    fig.suptitle('Comparación Aluminio 6061 vs Acero Inoxidable 304',
                 fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    # Guardar
    if guardar:
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 7: DISTRIBUCIÓN ESPACIAL COMPLETA
# =============================================================================

def graficar_distribucion_espacial_completa(
    resultados: Dict,
    mallas: Dict,
    params: 'Parametros',
    tiempo_idx: int = -1,
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> plt.Figure:
    """
    Grafica la distribución espacial completa del sistema: placa + aletas + agua.
    
    Vista frontal (x-y) mostrando:
    - Placa base con su perfil de temperatura
    - 3 aletas cilíndricas en sus posiciones reales
    - Agua fluyendo entre las aletas
    
    Args:
        resultados (Dict): Resultados de la simulación
        mallas (Dict): Mallas del sistema
        params (Parametros): Parámetros
        tiempo_idx (int): Índice temporal (default: -1)
        guardar (bool): Si guardar
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar
    
    Returns:
        plt.Figure: Objeto de figura
    
    Notes:
        - Muestra la geometría real del sistema
        - Incluye escala de temperatura unificada
        - Vista en corte longitudinal (x-y)
    """
    # Validaciones
    assert tiempo_idx < len(resultados['tiempo']), "tiempo_idx fuera de rango"
    
    tiempo = resultados['tiempo'][tiempo_idx]
    T_p = np.asarray(resultados['T_placa'][tiempo_idx], dtype=float) - 273.15  # °C
    T_a = [np.asarray(T, dtype=float) - 273.15 for T in resultados['T_aletas'][tiempo_idx]]
    T_f = np.asarray(resultados['T_fluido'][tiempo_idx], dtype=float) - 273.15
    
    # Parámetros geométricos (en mm para visualización)
    L_x = params.L_x * 1000  # 30 mm
    e_base = params.e_base * 1000  # 10 mm
    r = params.r * 1000  # 4 mm
    x_aletas = [params.x_aleta_1 * 1000, params.x_aleta_2 * 1000, params.x_aleta_3 * 1000]
    
    # Rango de temperatura para escala común
    T_min = min(T_p.min(), min([Ta.min() for Ta in T_a]), T_f.min())
    T_max = max(T_p.max(), max([Ta.max() for Ta in T_a]), T_f.max())
    
    # Crear figura grande
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    # =========================================================================
    # PANEL 1: VISTA FRONTAL COMPLETA (x-y)
    # =========================================================================
    
    # 1. Dibujar la placa base
    if mallas['placa']['x'].ndim == 2:
        x_p = mallas['placa']['x'] * 1000
        y_p = mallas['placa']['y'] * 1000
    else:
        x_p_1d = mallas['placa']['x'] * 1000
        y_p_1d = mallas['placa']['y'] * 1000
        x_p, y_p = np.meshgrid(x_p_1d, y_p_1d)
    
    # Placa: contorno filled
    im1 = ax1.contourf(x_p, y_p, T_p.T, levels=30, cmap='hot', 
                       vmin=T_min, vmax=T_max, alpha=0.9)
    
    # 2. Dibujar las 3 aletas en sus posiciones
    for k, x_center in enumerate(x_aletas):
        # Coordenadas polares de la aleta (semicírculo superior)
        theta_aleta = np.linspace(0, np.pi, 100)
        x_aleta = x_center + r * np.cos(theta_aleta)
        y_aleta = e_base + r * np.sin(theta_aleta)
        
        # Temperatura promedio de la aleta para color
        T_aleta_mean = T_a[k].mean()
        
        # Rellenar semicírculo con color según temperatura
        color_aleta = plt.cm.hot((T_aleta_mean - T_min) / (T_max - T_min))
        ax1.fill(x_aleta, y_aleta, color=color_aleta, alpha=0.9, 
                edgecolor='black', linewidth=1.5)
        
        # Etiqueta
        ax1.text(x_center, e_base + r + 0.5, f'Aleta {k+1}\n{T_aleta_mean:.1f}°C',
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # 3. Indicar zona de agua (entre placa y aletas)
    # Dibujar rectángulo semitransparente para agua
    T_agua_mean = T_f.mean()
    color_agua = plt.cm.cool(0.5)  # Azul para agua
    
    # Agua en toda la longitud, desde y=e_base hasta parte superior
    ax1.axhspan(e_base, e_base + 2*r, alpha=0.15, color='cyan', 
                label=f'Zona de agua (T≈{T_agua_mean:.1f}°C)')
    
    # 4. Añadir líneas de referencia
    ax1.axhline(e_base, color='black', linestyle='--', linewidth=2, 
                alpha=0.7, label='Superficie placa-agua')
    
    # Configurar ejes
    ax1.set_xlabel('Posición x (mm)', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Posición y (mm)', fontweight='bold', fontsize=12)
    ax1.set_title(f'Distribución Espacial de Temperatura - Vista Frontal - t={tiempo:.2f}s',
                  fontsize=14, fontweight='bold')
    ax1.set_xlim(0, L_x)
    ax1.set_ylim(0, e_base + 2*r + 1)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Colorbar
    cbar1 = plt.colorbar(im1, ax=ax1, label='Temperatura (°C)', pad=0.02)
    
    # =========================================================================
    # PANEL 2: PERFILES DE TEMPERATURA EN CORTES VERTICALES
    # =========================================================================
    
    # Extraer perfiles verticales en las posiciones de las aletas
    x_p_1d = mallas['placa']['x'] if mallas['placa']['x'].ndim == 1 else mallas['placa']['x'][0, :]
    y_p_1d = mallas['placa']['y'] if mallas['placa']['y'].ndim == 1 else mallas['placa']['y'][:, 0]
    
    for k, x_center in enumerate(x_aletas):
        # Encontrar índice más cercano en x
        idx_x = np.argmin(np.abs(x_p_1d * 1000 - x_center))
        
        # Perfil vertical de la placa
        T_perfil_placa = T_p[idx_x, :]
        
        # Graficar perfil de placa
        ax2.plot(T_perfil_placa, y_p_1d * 1000, 
                linewidth=2.5, marker='o', markersize=4, 
                label=f'Placa en x={x_center:.1f}mm (Aleta {k+1})',
                alpha=0.8)
        
        # Agregar punto de temperatura promedio de aleta
        T_aleta_mean = T_a[k].mean()
        ax2.scatter([T_aleta_mean], [e_base + r], s=200, marker='^',
                   edgecolors='black', linewidths=2, alpha=0.8,
                   label=f'Aleta {k+1} (T≈{T_aleta_mean:.1f}°C)')
    
    # Líneas de referencia
    ax2.axhline(e_base, color='black', linestyle='--', linewidth=1.5, 
                alpha=0.5, label='Interfaz placa-agua')
    ax2.axhline(e_base + r, color='gray', linestyle=':', linewidth=1.5,
                alpha=0.5, label='Centro aletas')
    
    ax2.set_xlabel('Temperatura (°C)', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Posición y (mm)', fontweight='bold', fontsize=12)
    ax2.set_title('Perfiles de Temperatura en Cortes Verticales',
                  fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9, framealpha=0.9, ncol=2)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_ylim(0, e_base + 2*r + 1)
    
    # Título general
    fig.suptitle(f'Sistema Completo de Enfriamiento - {params.material}',
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"distribucion_espacial_{params.material}_t{tiempo:.2f}s.png"
        ruta = DIR_FIGURAS / nombre_archivo
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        print(f"✅ Figura guardada: {ruta}")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


# =============================================================================
# FUNCIÓN 8: ANIMACIÓN
# =============================================================================

def crear_animacion(
    resultados: Dict,
    mallas: Dict,
    params: 'Parametros',
    fps: int = 10,
    guardar: bool = True,
    nombre_archivo: Optional[str] = None,
    mostrar: bool = False
) -> animation.FuncAnimation:
    """
    Crea una animación de la evolución temporal del sistema.
    
    Args:
        resultados (Dict): Resultados de la simulación
        mallas (Dict): Mallas del sistema
        params (Parametros): Parámetros
        fps (int): Frames por segundo (default: 10)
        guardar (bool): Si guardar como video/GIF
        nombre_archivo (str): Nombre del archivo
        mostrar (bool): Si mostrar interactivamente
    
    Returns:
        animation.FuncAnimation: Objeto de animación
    
    Notes:
        - Requiere ffmpeg instalado para guardar como MP4
        - Puede ser lento para muchos frames
    """
    print("⏳ Creando animación...")
    
    tiempo = resultados['tiempo']
    T_fluido = resultados['T_fluido']
    T_placa = resultados['T_placa']
    T_aletas = resultados['T_aletas']
    
    # Configurar figura
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, :])  # Evolución temporal
    ax2 = fig.add_subplot(gs[1, 0])  # Perfil fluido
    ax3 = fig.add_subplot(gs[1, 1])  # Campo placa
    ax4 = fig.add_subplot(gs[1, 2])  # Perfil aleta
    
    # Calcular límites globales
    T_min = min(T.min() for T in T_placa) - 273.15
    T_max = max(T.max() for T in T_placa) - 273.15
    
    # Inicializar líneas/imágenes
    line_f, = ax1.plot([], [], 'b-', linewidth=2, label='Fluido')
    line_p, = ax1.plot([], [], 'r-', linewidth=2, label='Placa')
    line_a, = ax1.plot([], [], 'g-', linewidth=2, label='Aletas')
    
    def init():
        ax1.set_xlim(0, tiempo[-1])
        ax1.set_ylim(T_min - 5, T_max + 5)
        ax1.set_xlabel('Tiempo (s)', fontweight='bold')
        ax1.set_ylabel('Temperatura (°C)', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        return line_f, line_p, line_a
    
    def update(frame):
        # Actualizar temperaturas promedio hasta el frame actual
        t_slice = tiempo[:frame+1]
        T_f_slice = [T.mean() - 273.15 for T in T_fluido[:frame+1]]
        T_p_slice = [T.mean() - 273.15 for T in T_placa[:frame+1]]
        T_a_slice = [np.mean([Ta.mean() for Ta in Tas]) - 273.15 
                     for Tas in T_aletas[:frame+1]]
        
        line_f.set_data(t_slice, T_f_slice)
        line_p.set_data(t_slice, T_p_slice)
        line_a.set_data(t_slice, T_a_slice)
        
        # Actualizar título con tiempo actual
        fig.suptitle(f'{params.material} - t = {tiempo[frame]:.2f} s', 
                     fontsize=14, fontweight='bold')
        
        # Actualizar perfil de fluido
        ax2.clear()
        x_f = mallas['fluido']['x'] * 1000
        T_f_frame = T_fluido[frame] - 273.15
        ax2.plot(x_f, T_f_frame, 'b-', linewidth=2)
        ax2.set_xlabel('x (mm)')
        ax2.set_ylabel('T (°C)')
        ax2.set_title('Fluido')
        ax2.set_ylim(T_min - 5, T_max + 5)
        ax2.grid(True, alpha=0.3)
        
        # Actualizar campo de placa
        ax3.clear()
        x_p = mallas['placa']['x'] * 1000
        y_p = mallas['placa']['y'] * 1000
        T_p_frame = T_placa[frame] - 273.15
        im = ax3.contourf(x_p, y_p, T_p_frame.T, levels=15, cmap='hot', 
                          vmin=T_min, vmax=T_max)
        ax3.set_xlabel('x (mm)')
        ax3.set_ylabel('y (mm)')
        ax3.set_title('Placa')
        ax3.set_aspect('equal')
        
        # Actualizar perfil de aleta
        ax4.clear()
        r_a = mallas['aletas'][0]['r'][:, 0] * 1000
        T_a_frame = T_aletas[frame][0][:, 0] - 273.15
        ax4.plot(r_a, T_a_frame, 'g-', linewidth=2)
        ax4.set_xlabel('r (mm)')
        ax4.set_ylabel('T (°C)')
        ax4.set_title('Aleta 1')
        ax4.set_ylim(T_min - 5, T_max + 5)
        ax4.grid(True, alpha=0.3)
        
        return line_f, line_p, line_a
    
    # Crear animación
    n_frames = len(tiempo)
    anim = animation.FuncAnimation(
        fig, update, init_func=init, frames=n_frames,
        interval=1000/fps, blit=False, repeat=True
    )
    
    # Guardar
    if guardar:
        if nombre_archivo is None:
            nombre_archivo = f"animacion_{params.material}.gif"
        ruta = DIR_FIGURAS / nombre_archivo
        
        print(f"⏳ Guardando animación (puede tardar varios minutos)...")
        try:
            if nombre_archivo.endswith('.gif'):
                anim.save(ruta, writer='pillow', fps=fps, dpi=100)
            elif nombre_archivo.endswith('.mp4'):
                anim.save(ruta, writer='ffmpeg', fps=fps, dpi=100)
            print(f"✅ Animación guardada: {ruta}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar animación: {e}")
            print("   Instala ffmpeg o usa formato .gif")
    
    if mostrar:
        plt.show()
    else:
        plt.close(fig)
    
    return anim


# =============================================================================
# FUNCIÓN 8: REPORTE COMPLETO
# =============================================================================

def generar_reporte_completo(
    resultados: Dict,
    mallas: Dict,
    params: 'Parametros',
    epsilon: float = 1e-3,
    crear_animacion_gif: bool = False,
    verbose: bool = True
) -> Dict[str, Path]:
    """
    Genera un reporte completo con todas las visualizaciones del sistema.
    
    Args:
        resultados (Dict): Resultados de la simulación
        mallas (Dict): Mallas del sistema
        params (Parametros): Parámetros
        epsilon (float): Criterio de convergencia
        crear_animacion_gif (bool): Si crear animación (lento)
        verbose (bool): Si imprimir progreso
    
    Returns:
        Dict[str, Path]: Diccionario con rutas a todas las figuras generadas
    
    Notes:
        - Genera 6-7 figuras automáticamente
        - Guarda todo en resultados/figuras/
        - Retorna diccionario con rutas para referencia
    """
    if verbose:
        print("=" * 70)
        print("GENERANDO REPORTE COMPLETO DE VISUALIZACIONES")
        print("=" * 70)
    
    rutas = {}
    
    # 1. Evolución temporal
    if verbose:
        print("\n1. Generando evolución temporal...")
    fig = graficar_evolucion_temporal(resultados, params, guardar=True, mostrar=False)
    rutas['evolucion'] = DIR_FIGURAS / f"evolucion_temporal_{params.material}.png"
    
    # 2. Perfiles espaciales
    if verbose:
        print("2. Generando perfiles espaciales...")
    fig = graficar_perfiles_espaciales(resultados, mallas, params, 
                                        guardar=True, mostrar=False)
    rutas['perfiles'] = DIR_FIGURAS / f"perfiles_espaciales_{params.material}_t{resultados['tiempo'][-1]:.2f}s.png"
    
    # 3. Campos 2D
    if verbose:
        print("3. Generando campos 2D...")
    try:
        fig = graficar_campo_2d(resultados, mallas, params, 
                                guardar=True, mostrar=False)
        rutas['campos'] = DIR_FIGURAS / f"campos_2d_{params.material}_t{resultados['tiempo'][-1]:.2f}s.png"
    except Exception as e:
        if verbose:
            print(f"   ⚠️ No se pudo generar campos 2D: {e}")
    
    # 4. Balance energético (si está disponible)
    if 'metricas' in resultados and 'balance' in resultados['metricas'] and \
       len(resultados['metricas']['balance']) > 0:
        if verbose:
            print("4. Generando balance energético...")
        fig = graficar_balance_energetico(resultados, params, 
                                           guardar=True, mostrar=False)
        rutas['balance'] = DIR_FIGURAS / f"balance_energetico_{params.material}.png"
    
    # 5. Distribución espacial completa
    if verbose:
        print("5. Generando distribución espacial completa...")
    try:
        fig = graficar_distribucion_espacial_completa(resultados, mallas, params,
                                                       guardar=True, mostrar=False)
        rutas['distribucion'] = DIR_FIGURAS / f"distribucion_espacial_{params.material}_t{resultados['tiempo'][-1]:.2f}s.png"
    except Exception as e:
        if verbose:
            print(f"   ⚠️ No se pudo generar distribución espacial: {e}")
    
    # 6. Convergencia
    if verbose:
        print("6. Generando gráfico de convergencia...")
    fig = graficar_convergencia(resultados, params, epsilon=epsilon,
                                 guardar=True, mostrar=False)
    rutas['convergencia'] = DIR_FIGURAS / f"convergencia_{params.material}.png"
    
    # 7. Animación (opcional)
    if crear_animacion_gif:
        if verbose:
            print("7. Creando animación (esto puede tardar)...")
        try:
            anim = crear_animacion(resultados, mallas, params, 
                                   guardar=True, mostrar=False)
            rutas['animacion'] = DIR_FIGURAS / f"animacion_{params.material}.gif"
        except Exception as e:
            if verbose:
                print(f"   ⚠️ No se pudo crear animación: {e}")
    
    if verbose:
        print("\n" + "=" * 70)
        print("✅ REPORTE COMPLETO GENERADO")
        print("=" * 70)
        print(f"\n📁 Figuras guardadas en: {DIR_FIGURAS}")
        print(f"   Total de figuras: {len(rutas)}")
        for nombre, ruta in rutas.items():
            print(f"   - {nombre}: {ruta.name}")
    
    return rutas


# =============================================================================
# FUNCIÓN AUXILIAR: CARGAR RESULTADOS
# =============================================================================

def cargar_resultados(nombre_archivo: str) -> Dict:
    """
    Carga resultados desde archivo .npz.
    
    Args:
        nombre_archivo (str): Nombre del archivo (ej: "resultados_Al.npz")
    
    Returns:
        Dict: Diccionario con resultados
    
    Examples:
        >>> resultados = cargar_resultados("resultados_Al.npz")
        >>> print(resultados.keys())
    
    Notes:
        - Soporta dos formatos de claves:
          1. Formato nuevo: 'T_fluido', 'T_placa', 'T_aletas', 'convergencia', 'metricas'
          2. Formato antiguo: 'T_fluido_historia', 'convergencia_alcanzada', etc.
    """
    from pathlib import Path
    
    ruta = Path(__file__).parent.parent / "resultados" / "datos" / nombre_archivo
    
    assert ruta.exists(), f"Archivo no encontrado: {ruta}"
    
    data = np.load(ruta, allow_pickle=True)
    
    # Determinar formato del archivo
    if 'T_fluido' in data.files:
        # Formato nuevo (solucionador.py moderno)
        resultados = {
            'tiempo': data['tiempo'],
            'T_fluido': data['T_fluido'],
            'T_placa': data['T_placa'],
            'T_aletas': data['T_aletas'],
            'convergencia': data['convergencia'].item(),
            'metricas': data['metricas'].item()
        }
    elif 'T_fluido_historia' in data.files:
        # Formato antiguo (solucionador.py anterior)
        resultados = {
            'tiempo': data['tiempo'],
            'T_fluido': data['T_fluido_historia'],
            'T_placa': data['T_placa_historia'],
            'T_aletas': data['T_aletas_historia'],
            'convergencia': {
                'alcanzada': bool(data['convergencia_alcanzada']),
                't_convergencia': float(data['t_convergencia']) if 't_convergencia' in data.files else None
            },
            'metricas': {
                'balance': data['balance_energetico'].tolist() if 'balance_energetico' in data.files else []
            }
        }
    else:
        raise ValueError(f"Formato de archivo no reconocido. Claves: {data.files}")
    
    print(f"✅ Resultados cargados desde: {ruta.name}")
    return resultados


# =============================================================================
# MAIN - EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso del módulo de visualización.
    
    Este bloque muestra cómo:
    1. Cargar resultados desde archivo
    2. Generar visualizaciones individuales
    3. Crear reporte completo
    4. Comparar materiales
    """
    import sys
    from pathlib import Path
    
    # Agregar directorio padre al path
    PROJECT_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(PROJECT_DIR))
    
    from src.parametros import Parametros
    from src.mallas import generar_todas_mallas
    
    print("=" * 70)
    print("EJEMPLO DE USO: Módulo de Visualización")
    print("=" * 70)
    
    # Verificar si existen resultados guardados (soportar ambos nombres)
    archivo_al = PROJECT_DIR / "resultados" / "datos" / "resultados_Al.npz"
    archivo_al_alt = PROJECT_DIR / "resultados" / "datos" / "resultados_Aluminio.npz"
    archivo_ss = PROJECT_DIR / "resultados" / "datos" / "resultados_SS.npz"
    archivo_ss_alt = PROJECT_DIR / "resultados" / "datos" / "resultados_AceroInoxidable.npz"
    
    # Determinar qué archivo usar
    if archivo_al.exists():
        nombre_al = "resultados_Al.npz"
    elif archivo_al_alt.exists():
        nombre_al = "resultados_Aluminio.npz"
        archivo_al = archivo_al_alt
    else:
        print("\n⚠️ No se encontró archivo de resultados de Aluminio")
        print("   Ejecuta primero una simulación con solucionador.py")
        print(f"   Buscando: {archivo_al} o {archivo_al_alt}")
        sys.exit(0)
    
    # Cargar resultados y parámetros
    print(f"\n1. Cargando resultados de Aluminio ({nombre_al})...")
    resultados_al = cargar_resultados(nombre_al)
    params_al = Parametros(material='Al')
    mallas_al = generar_todas_mallas(params_al)
    
    # Generar reporte completo
    print("\n2. Generando reporte completo de visualizaciones...")
    rutas = generar_reporte_completo(
        resultados_al, 
        mallas_al, 
        params_al,
        epsilon=1e-3,
        crear_animacion_gif=False,  # Cambiar a True para crear animación
        verbose=True
    )
    
    # Si existe resultados de SS, comparar
    if archivo_ss.exists():
        nombre_ss = "resultados_SS.npz"
    elif archivo_ss_alt.exists():
        nombre_ss = "resultados_AceroInoxidable.npz"
        archivo_ss = archivo_ss_alt
    else:
        nombre_ss = None
    
    if nombre_ss:
        print(f"\n3. Cargando resultados de Acero Inoxidable ({nombre_ss})...")
        resultados_ss = cargar_resultados(nombre_ss)
        params_ss = Parametros(material='SS')
        
        print("\n4. Generando comparación entre materiales...")
        fig = comparar_materiales(
            resultados_al, resultados_ss,
            params_al, params_ss,
            guardar=True, mostrar=False
        )
    
    print("\n" + "=" * 70)
    print("✅ VISUALIZACIONES COMPLETADAS")
    print("=" * 70)
    print(f"\n📊 Se generaron {len(rutas)} figuras en:")
    print(f"   {DIR_FIGURAS}")
    print("\nPuedes visualizarlas abriendo los archivos .png")
