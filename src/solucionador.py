#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de solución temporal del sistema completo de enfriamiento GPU.

Este módulo implementa el bucle temporal maestro que integra los solvers
de fluido, placa y aletas, con manejo de múltiples escalas temporales y
criterio de convergencia a estado estacionario.

Características:
- Manejo de dt múltiples (placa vs aletas)
- Acoplamiento térmico fluido → placa → aletas
- Criterio de convergencia físico (max|dT/dt| < ε)
- Guardado eficiente de resultados
- Balance energético para validación
- Soporte para múltiples materiales

Autor: Sistema de Enfriamiento GPU - Proyecto IQ-0331
Fecha: 2025-10-05
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
import os
from pathlib import Path

from src.parametros import Parametros
from src.fluido import inicializar_fluido, actualizar_fluido
from src.placa import inicializar_placa, actualizar_placa
from src.aletas import inicializar_aleta, actualizar_aleta
from src.acoplamiento import (
    extraer_temperatura_superficie_placa,
    interpolar_temperatura_para_fluido,
    aplicar_acoplamiento_placa_aletas
)


def calcular_dt_aletas(params: Parametros, mallas: Dict) -> float:
    """
    Calcula el paso de tiempo restrictivo para aletas en coordenadas cilíndricas.
    
    En coordenadas cilíndricas, el criterio de Fourier es más restrictivo
    en r_min (primer nodo después del centro) debido al término 1/r² en
    la difusión angular.
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
        mallas (Dict): Diccionario con todas las mallas
    
    Returns:
        float: Paso de tiempo máximo permitido para aletas [s]
    
    Notes:
        - Criterio de estabilidad: Fo_r + Fo_θ(max) < 0.5
        - Fo_θ es máximo en r_min = dr (más restrictivo)
        - Se usa 80% del dt_max como margen de seguridad
    
    References:
        Ver contexto/05_discretizacion_numerica.md sección 3.3
    """
    alpha = params.alpha_s
    dr = mallas['aletas'][0]['dr']
    dtheta = mallas['aletas'][0]['dtheta']
    r_min = dr  # Primer nodo después del centro (j=1)
    
    # Factor de estabilidad: α * (1/Δr² + 1/(r_min*Δθ)²)
    factor_estabilidad = alpha * (1.0 / dr**2 + 1.0 / ((r_min * dtheta)**2))
    
    # dt_max para Fo_total < 0.5
    dt_max = 0.5 / factor_estabilidad
    
    # Usar 80% del máximo (margen de seguridad)
    dt_seguro = 0.8 * dt_max
    
    # Validaciones
    assert dt_seguro > 0, "dt_aletas debe ser positivo"
    assert dt_seguro < params.dt, \
        f"dt_aletas ({dt_seguro:.2e}) debe ser < dt_placa ({params.dt:.2e})"
    
    return dt_seguro


def verificar_convergencia(T_old: Dict,
                           T_new: Dict,
                           dt: float,
                           epsilon: float) -> Tuple[bool, float]:
    """
    Verifica si el sistema alcanzó el estado estacionario.
    
    El criterio de convergencia es:
        max|dT/dt| < ε
    
    donde dT/dt se calcula en todos los dominios (fluido, placa, aletas).
    
    Args:
        T_old (Dict): Temperaturas en paso anterior
            - 'fluido': ndarray (Nx,)
            - 'placa': ndarray (Nx, Ny)
            - 'aletas': list de 3 ndarrays (Ntheta, Nr)
        T_new (Dict): Temperaturas en paso actual (misma estructura)
        dt (float): Paso de tiempo usado [s]
        epsilon (float): Tolerancia para convergencia [K/s]
    
    Returns:
        Tuple[bool, float]: (converged, max_rate)
            - converged: True si max|dT/dt| < epsilon
            - max_rate: Tasa máxima de cambio [K/s]
    
    Notes:
        - El criterio se evalúa sobre TODOS los nodos del sistema
        - Se usa la norma infinito (máximo absoluto)
    
    References:
        Ver contexto/00_guia_implementacion.md sección "Métricas de Evaluación"
    """
    # Validaciones de entrada
    assert dt > 0, "dt debe ser positivo"
    assert epsilon > 0, "epsilon debe ser positivo"
    assert 'fluido' in T_old and 'fluido' in T_new, "Falta campo 'fluido'"
    assert 'placa' in T_old and 'placa' in T_new, "Falta campo 'placa'"
    assert 'aletas' in T_old and 'aletas' in T_new, "Falta campo 'aletas'"
    
    # Calcular tasa de cambio en cada dominio: |dT/dt| = |T_new - T_old| / dt
    rate_fluido = np.abs(T_new['fluido'] - T_old['fluido']) / dt
    rate_placa = np.abs(T_new['placa'] - T_old['placa']) / dt
    rate_aletas = [np.abs(T_new['aletas'][k] - T_old['aletas'][k]) / dt 
                   for k in range(3)]
    
    # Máximo global sobre todos los dominios
    max_rate = max(
        rate_fluido.max(),
        rate_placa.max(),
        max(r.max() for r in rate_aletas)
    )
    
    # Verificar convergencia
    converged = max_rate < epsilon
    
    # Validaciones
    assert not np.isnan(max_rate), "max_rate es NaN"
    assert not np.isinf(max_rate), "max_rate es Inf"
    
    return converged, max_rate


def guardar_estado(tiempo: float,
                   T_fluido: np.ndarray,
                   T_placa: np.ndarray,
                   T_aletas: List[np.ndarray],
                   historico: Dict) -> None:
    """
    Guarda el estado actual en el histórico de la simulación.
    
    Args:
        tiempo (float): Tiempo actual [s]
        T_fluido (ndarray): Campo de temperatura del fluido [K]
        T_placa (ndarray): Campo de temperatura de la placa [K]
        T_aletas (List[ndarray]): Lista con 3 campos de temperatura de aletas [K]
        historico (Dict): Diccionario donde se almacenarán los datos
    
    Notes:
        - Se guardan COPIAS de los arrays para evitar referencias
        - El histórico se va llenando conforme avanza la simulación
    """
    historico['tiempo'].append(tiempo)
    historico['T_fluido'].append(T_fluido.copy())
    historico['T_placa'].append(T_placa.copy())
    historico['T_aletas'].append([T.copy() for T in T_aletas])


def calcular_balance_energetico(T_fluido: np.ndarray,
                                T_placa: np.ndarray,
                                T_aletas: List[np.ndarray],
                                T_fluido_old: np.ndarray,
                                T_placa_old: np.ndarray,
                                T_aletas_old: List[np.ndarray],
                                params: Parametros,
                                mallas: Dict,
                                dt: float) -> Dict:
    """
    Calcula el balance energético global del sistema.
    
    Balance de energía:
        Q_in = Q_out + dE/dt
    
    Donde:
        - Q_in: Calor entrante desde agua caliente
        - Q_out: Calor saliente hacia aire ambiente
        - dE/dt: Tasa de cambio de energía interna
    
    Args:
        T_fluido, T_placa, T_aletas: Temperaturas actuales [K]
        T_fluido_old, T_placa_old, T_aletas_old: Temperaturas anteriores [K]
        params: Parámetros del sistema
        mallas: Diccionario con las mallas
        dt: Paso de tiempo [s]
    
    Returns:
        Dict: Balance energético con claves:
            - 'Q_in': Potencia entrante [W]
            - 'Q_out': Potencia saliente [W]
            - 'dE_dt': Tasa de cambio de energía [W]
            - 'error_relativo': Error relativo del balance [-]
    
    Notes:
        - Se usa para validar la correctitud de la simulación
        - Un error < 5-10% es aceptable en esquemas explícitos
    """
    # Q_in: Calor desde el agua (entrada - salida)
    T_in = params.T_f_in
    T_out = T_fluido[-1]
    m_dot = params.rho_agua * params.u * params.W * params.e_agua  # kg/s
    Q_in = m_dot * params.cp_agua * (T_in - T_out)  # W
    
    # Q_out: Calor hacia el aire (convección desde superficies)
    # Superficie superior de la placa (y=e_base)
    # T_placa tiene shape (Nx, Ny), superficie aire está en [:, -1]
    T_sup_placa = T_placa[:, -1].mean()  # Temperatura promedio superficie aire placa
    A_placa_aire = params.L_x * params.W
    Q_out_placa = params.h_aire * A_placa_aire * (T_sup_placa - params.T_inf)
    
    # Superficies de las 3 aletas
    Q_out_aletas = 0.0
    A_aleta = np.pi * params.r * params.W  # Área semicircular por aleta
    for k in range(3):
        T_sup_aleta = T_aletas[k][:, -1].mean()  # Superficie r=R
        Q_out_aletas += params.h_aire * A_aleta * (T_sup_aleta - params.T_inf)
    
    Q_out = Q_out_placa + Q_out_aletas  # W
    
    # dE/dt: Tasa de cambio de energía interna
    # E = ρ * c_p * V * T
    dx_fluido = mallas['fluido']['dx']
    A_fluido = params.W * params.e_agua
    V_fluido_nodo = dx_fluido * A_fluido
    
    dx_placa = mallas['placa']['dx']
    dy_placa = mallas['placa']['dy']
    V_placa_nodo = dx_placa * dy_placa * params.W
    
    dr = mallas['aletas'][0]['dr']
    dtheta = mallas['aletas'][0]['dtheta']
    # Volumen de un elemento cilíndrico: dV = r * dr * dθ * dz
    # (se calculará por nodo)
    
    # Cambio de energía en fluido
    dT_fluido = T_fluido - T_fluido_old
    dE_fluido = (params.rho_agua * params.cp_agua * V_fluido_nodo * dT_fluido).sum()
    
    # Cambio de energía en placa
    dT_placa = T_placa - T_placa_old
    dE_placa = (params.rho_s * params.cp_s * V_placa_nodo * dT_placa).sum()
    
    # Cambio de energía en aletas
    dE_aletas = 0.0
    r_grid = mallas['aletas'][0]['r']
    for k in range(3):
        dT_aleta = T_aletas[k] - T_aletas_old[k]
        for j in range(len(r_grid)):
            r_j = r_grid[j] if j > 0 else dr/2  # En centro, usar r promedio
            dV_nodo = r_j * dr * dtheta * params.W
            dE_aletas += (params.rho_s * params.cp_s * dV_nodo * dT_aleta[:, j]).sum()
    
    dE_dt = (dE_fluido + dE_placa + dE_aletas) / dt  # W
    
    # Error relativo: |Q_in - Q_out - dE/dt| / Q_in
    error_absoluto = abs(Q_in - Q_out - dE_dt)
    error_relativo = error_absoluto / abs(Q_in) if abs(Q_in) > 1e-6 else 0.0
    
    return {
        'Q_in': Q_in,
        'Q_out': Q_out,
        'dE_dt': dE_dt,
        'error_relativo': error_relativo
    }


def guardar_resultados(resultados: Dict,
                      params: Parametros,
                      directorio: str = "resultados/datos") -> str:
    """
    Guarda los resultados de la simulación en un archivo .npz.
    
    Si el archivo ya existe, se sobreescribe.
    
    Args:
        resultados (Dict): Diccionario con los resultados de la simulación
        params (Parametros): Parámetros del sistema (para nombre de archivo)
        directorio (str): Directorio donde guardar (relativo al proyecto)
    
    Returns:
        str: Ruta del archivo guardado
    
    Notes:
        - Formato: resultados/datos/resultados_<material>.npz
        - Usa np.savez_compressed para reducir tamaño
    """
    # Crear directorio si no existe
    Path(directorio).mkdir(parents=True, exist_ok=True)
    
    # Nombre de archivo según material
    material_str = "Aluminio" if params.material == "Al" else "AceroInox"
    nombre_archivo = f"resultados_{material_str}.npz"
    ruta_completa = os.path.join(directorio, nombre_archivo)
    
    # Preparar datos para guardar
    # Los arrays se guardan directamente, las listas se convierten a object arrays
    datos_guardar = {
        'tiempo': resultados['tiempo'],
        'T_fluido_historia': np.array(resultados['T_fluido'], dtype=object),
        'T_placa_historia': np.array(resultados['T_placa'], dtype=object),
        'T_aletas_historia': np.array(resultados['T_aletas'], dtype=object),
        'convergencia_alcanzada': resultados['convergencia']['alcanzada'],
        't_convergencia': resultados['convergencia']['t_convergencia'] 
                         if resultados['convergencia']['t_convergencia'] is not None 
                         else -1.0,
        'material': material_str,
        'alpha': params.alpha_s,
        'dt_placa': params.dt
    }
    
    # Agregar métricas si existen
    if 'metricas' in resultados:
        datos_guardar['balance_energetico'] = np.array(resultados['metricas']['balance'], dtype=object)
    
    # Guardar (sobreescribe si existe)
    np.savez_compressed(ruta_completa, **datos_guardar)
    
    return ruta_completa


def resolver_sistema(params: Parametros,
                     mallas: Dict,
                     t_max: float = 30.0,
                     epsilon: float = 1e-3,
                     guardar_cada: int = 100,
                     calcular_balance: bool = True,
                     verbose: bool = True,
                     progress_file: str = None) -> Dict:
    """
    Resuelve el sistema completo hasta t_max o hasta convergencia.
    
    Integra los solvers de fluido (1D), placa (2D cartesiano) y aletas
    (2D cilíndrico) en un bucle temporal con manejo de múltiples escalas
    temporales y criterio de convergencia a estado estacionario.
    
    Args:
        params (Parametros): Objeto con parámetros del sistema
        mallas (Dict): Diccionario con todas las mallas del sistema
        t_max (float): Tiempo máximo de simulación [s]. Default: 30.0
        epsilon (float): Tolerancia para convergencia [K/s]. Default: 1e-3
        guardar_cada (int): Guardar datos cada N pasos. Default: 100
        calcular_balance (bool): Si calcular balance energético. Default: True
        verbose (bool): Si imprimir progreso. Default: True
    
    Returns:
        Dict: Resultados de la simulación con claves:
            - 'tiempo': ndarray con tiempos guardados [s]
            - 'T_fluido': lista de campos de temperatura del fluido [K]
            - 'T_placa': lista de campos de temperatura de la placa [K]
            - 'T_aletas': lista de [3 aletas] en cada tiempo [K]
            - 'convergencia': dict con 'alcanzada' (bool) y 't_convergencia' (float)
            - 'metricas': dict con estadísticas de evolución
    
    Algorithm:
        1. Inicialización de campos de temperatura
        2. Cálculo de dt restrictivo para aletas
        3. Bucle temporal:
           a. Actualizar fluido (Upwind + acople con placa)
           b. Actualizar placa (FTCS + BCs Robin)
           c. Actualizar aletas (FTCS cilíndrico con subpasos)
           d. Verificar convergencia
           e. Guardar datos
        4. Retornar resultados
    
    Notes:
        - dt_placa = 0.5 ms (definido en params)
        - dt_aletas ~ 0.031 ms (calculado dinámicamente)
        - Se requieren ~16 subpasos de aletas por cada paso de placa
        - Estado estacionario: max|dT/dt| < 1e-3 K/s
    
    Raises:
        AssertionError: Si alguna validación numérica falla
    
    References:
        Ver contexto/05_discretizacion_numerica.md sección 6
    """
    if verbose:
        print("=" * 70, flush=True)
        print("SOLVER TEMPORAL COMPLETO - Sistema de Enfriamiento GPU", flush=True)
        print("=" * 70, flush=True)
        print(flush=True)
    
    # =========================================================================
    # PASO 1: INICIALIZACIÓN
    # =========================================================================
    if verbose:
        print("📐 PASO 1: Inicializando campos de temperatura...", flush=True)
    
    T_fluido = inicializar_fluido(params, mallas)
    T_placa = inicializar_placa(params, mallas)
    T_aletas = [inicializar_aleta(params, mallas, k) for k in range(3)]
    
    if verbose:
        print(f"  ✅ Fluido: {T_fluido.shape} nodos @ {T_fluido.mean()-273.15:.1f}°C", flush=True)
        print(f"  ✅ Placa: {T_placa.shape} nodos @ {T_placa.mean()-273.15:.1f}°C", flush=True)
        print(f"  ✅ Aletas: 3 × {T_aletas[0].shape} nodos @ {T_aletas[0].mean()-273.15:.1f}°C", flush=True)
        print(flush=True)
    
    # =========================================================================
    # PASO 2: CONFIGURAR PASOS TEMPORALES
    # =========================================================================
    if verbose:
        print("⏱️  PASO 2: Configurando pasos temporales...", flush=True)
    
    dt_placa = params.dt
    dt_aletas = calcular_dt_aletas(params, mallas)
    n_subpasos_aletas = int(np.ceil(dt_placa / dt_aletas))
    dt_aletas_ajustado = dt_placa / n_subpasos_aletas  # Ajustar para sincronizar
    
    if verbose:
        print(f"  dt_placa: {dt_placa*1000:.3f} ms", flush=True)
        print(f"  dt_aletas: {dt_aletas*1000:.4f} ms", flush=True)
        print(f"  Subpasos de aletas por paso de placa: {n_subpasos_aletas}", flush=True)
        print(flush=True)
    
    # =========================================================================
    # PASO 3: CONFIGURAR SIMULACIÓN
    # =========================================================================
    if verbose:
        print("🔧 PASO 3: Configurando simulación...", flush=True)
    
    n_pasos_max = int(t_max / dt_placa)
    historico = {
        'tiempo': [],
        'T_fluido': [],
        'T_placa': [],
        'T_aletas': []
    }
    
    metricas = {
        'balance': [],
        'max_rate_historia': []
    }
    
    # Guardar estado inicial
    guardar_estado(0.0, T_fluido, T_placa, T_aletas, historico)
    
    if verbose:
        print(f"  Tiempo máximo: {t_max:.1f} s", flush=True)
        print(f"  Pasos máximos: {n_pasos_max}", flush=True)
        print(f"  Guardar cada: {guardar_cada} pasos", flush=True)
        print(f"  Criterio convergencia: max|dT/dt| < {epsilon:.1e} K/s", flush=True)
        print(flush=True)
    
    # =========================================================================
    # PASO 4: BUCLE TEMPORAL PRINCIPAL
    # =========================================================================
    if verbose:
        print("🚀 PASO 4: Ejecutando bucle temporal...", flush=True)
        print("-" * 70, flush=True)
        print(flush=True)
    
    converged = False
    
    for n in range(n_pasos_max):
        t_actual = (n + 1) * dt_placa
        
        # Guardar estado anterior para verificar convergencia
        T_fluido_old = T_fluido.copy()
        T_placa_old = T_placa.copy()
        T_aletas_old = [T.copy() for T in T_aletas]
        
        # ---------------------------------------------------------------------
        # 4.1. ACTUALIZAR FLUIDO
        # ---------------------------------------------------------------------
        # Extraer temperatura de superficie de la placa (y=0)
        T_sup_placa = extraer_temperatura_superficie_placa(T_placa, mallas, params)
        
        # Interpolar a la malla del fluido si es necesario
        T_sup_interpolada = interpolar_temperatura_para_fluido(
            T_sup_placa, mallas, params
        )
        
        # Actualizar fluido con esquema Upwind + acople
        T_fluido = actualizar_fluido(
            T_fluido, T_sup_interpolada, params, mallas, dt_placa
        )
        
        # ---------------------------------------------------------------------
        # 4.2. ACTUALIZAR PLACA
        # ---------------------------------------------------------------------
        T_placa = actualizar_placa(T_placa, T_fluido, params, mallas, dt_placa)
        
        # ---------------------------------------------------------------------
        # 4.3. ACTUALIZAR ALETAS (con subpasos)
        # ---------------------------------------------------------------------
        for _ in range(n_subpasos_aletas):
            # Aplicar acoplamiento placa → aletas (BCs en θ=0,π)
            T_aletas = aplicar_acoplamiento_placa_aletas(
                T_placa, T_aletas, mallas, params
            )
            
            # Actualizar cada aleta
            for k in range(3):
                T_aletas[k] = actualizar_aleta(
                    T_aletas[k], params, mallas, k, dt_aletas_ajustado
                )
        
        # ---------------------------------------------------------------------
        # 4.4. VERIFICAR CONVERGENCIA
        # ---------------------------------------------------------------------
        T_old = {
            'fluido': T_fluido_old,
            'placa': T_placa_old,
            'aletas': T_aletas_old
        }
        T_new = {
            'fluido': T_fluido,
            'placa': T_placa,
            'aletas': T_aletas
        }
        
        converged, max_rate = verificar_convergencia(T_old, T_new, dt_placa, epsilon)
        metricas['max_rate_historia'].append(max_rate)
        
        # ---------------------------------------------------------------------
        # 4.5. CALCULAR BALANCE ENERGÉTICO (opcional)
        # ---------------------------------------------------------------------
        if calcular_balance and (n % guardar_cada == 0 or converged):
            balance = calcular_balance_energetico(
                T_fluido, T_placa, T_aletas,
                T_fluido_old, T_placa_old, T_aletas_old,
                params, mallas, dt_placa
            )
            # Agregar el tiempo actual al balance
            balance['tiempo'] = t
            metricas['balance'].append(balance)
        
        # ---------------------------------------------------------------------
        # 4.6. GUARDAR DATOS Y MOSTRAR PROGRESO
        # ---------------------------------------------------------------------
        if n % guardar_cada == 0 or converged or n == n_pasos_max - 1:
            guardar_estado(t_actual, T_fluido, T_placa, T_aletas, historico)
            
            # Temperaturas promedio para reporte
            T_f_avg = T_fluido.mean() - 273.15
            T_p_avg = T_placa.mean() - 273.15
            T_a_avg = np.mean([T.mean() for T in T_aletas]) - 273.15
            
            # Escribir progreso a archivo si se especificó
            if progress_file:
                try:
                    with open(progress_file, 'w') as f:
                        progreso_pct = (n + 1) / n_pasos_max * 100
                        f.write(f"{t_actual:.2f}|{max_rate:.2e}|{T_f_avg:.1f}|{T_p_avg:.1f}|{T_a_avg:.1f}|{progreso_pct:.1f}\n")
                except:
                    pass  # Si falla, no detener la simulación
            
            if verbose:
                print(f"  t={t_actual:6.2f}s | "
                      f"max|dT/dt|={max_rate:.2e} K/s | "
                      f"T_f={T_f_avg:5.1f}°C | "
                      f"T_p={T_p_avg:5.1f}°C | "
                      f"T_a={T_a_avg:5.1f}°C", flush=True)
                
                if calcular_balance and len(metricas['balance']) > 0:
                    err = metricas['balance'][-1]['error_relativo']
                    print(f"         Balance: Q_in={metricas['balance'][-1]['Q_in']:.1f}W, "
                          f"Error={err*100:.2f}%", flush=True)
        
        # ---------------------------------------------------------------------
        # 4.7. SALIR SI CONVERGIÓ
        # ---------------------------------------------------------------------
        if converged:
            if verbose:
                print(flush=True)
                print("=" * 70, flush=True)
                print(f"✅ CONVERGENCIA ALCANZADA en t={t_actual:.2f}s", flush=True)
                print(f"   max|dT/dt| = {max_rate:.2e} K/s < {epsilon:.1e} K/s", flush=True)
                print("=" * 70, flush=True)
            break
    
    # =========================================================================
    # PASO 5: PREPARAR Y RETORNAR RESULTADOS
    # =========================================================================
    if verbose:
        print(flush=True)
        print("📊 PASO 5: Preparando resultados...", flush=True)
    
    resultados = {
        'tiempo': np.array(historico['tiempo']),
        'T_fluido': historico['T_fluido'],
        'T_placa': historico['T_placa'],
        'T_aletas': historico['T_aletas'],
        'convergencia': {
            'alcanzada': converged,
            't_convergencia': t_actual if converged else None
        },
        'metricas': metricas
    }
    
    # Guardar a disco
    if verbose:
        print("  Guardando resultados a disco...", flush=True)
    
    ruta_guardado = guardar_resultados(resultados, params)
    
    if verbose:
        print(f"  ✅ Guardado en: {ruta_guardado}", flush=True)
        print(flush=True)
    
    return resultados


# =============================================================================
# SECCIÓN DE TESTING
# =============================================================================

if __name__ == "__main__":
    """
    Test del solucionador temporal completo.
    
    Simula el sistema de enfriamiento GPU hasta convergencia o t_max,
    guardando los resultados en disco.
    """
    import sys
    
    # Añadir directorio raíz al path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from src.mallas import generar_todas_mallas
    
    print("=" * 70)
    print("TEST: SOLVER TEMPORAL COMPLETO")
    print("Sistema de Enfriamiento GPU - Proyecto IQ-0331")
    print("=" * 70)
    print()
    
    # Configuración
    print("⚙️  Configuración del test:")
    print("  Material: Aluminio 6061")
    print("  Tiempo máximo: 30.0 s")
    print("  Criterio convergencia: 1e-3 K/s")
    print("  Balance energético: Activado")
    print()
    
    input("Presiona ENTER para iniciar la simulación...")
    print()
    
    # Crear parámetros y mallas
    params = Parametros(material="Al")
    mallas = generar_todas_mallas(params)
    
    # Resolver sistema
    resultados = resolver_sistema(
        params=params,
        mallas=mallas,
        t_max=30.0,
        epsilon=1e-3,
        guardar_cada=100,
        calcular_balance=True,
        verbose=True
    )
    
    # Resumen final
    print()
    print("=" * 70)
    print("✅ SIMULACIÓN COMPLETADA")
    print("=" * 70)
    print()
    
    print("📊 Resumen de resultados:")
    print(f"  Tiempo simulado: {resultados['tiempo'][-1]:.2f} s")
    print(f"  Pasos guardados: {len(resultados['tiempo'])}")
    print(f"  Convergencia: {'SÍ' if resultados['convergencia']['alcanzada'] else 'NO'}")
    
    if resultados['convergencia']['alcanzada']:
        t_conv = resultados['convergencia']['t_convergencia']
        print(f"  Tiempo de convergencia: {t_conv:.2f} s")
    
    print()
    
    # Temperaturas finales
    T_f_final = resultados['T_fluido'][-1]
    T_p_final = resultados['T_placa'][-1]
    T_a_final = resultados['T_aletas'][-1]
    
    print("🌡️  Temperaturas finales:")
    print(f"  Fluido:")
    print(f"    Entrada: {T_f_final[0] - 273.15:.1f}°C")
    print(f"    Salida: {T_f_final[-1] - 273.15:.1f}°C")
    print(f"    Promedio: {T_f_final.mean() - 273.15:.1f}°C")
    print()
    
    print(f"  Placa:")
    print(f"    Superficie agua (y=0): {T_p_final[:, 0].mean() - 273.15:.1f}°C")
    print(f"    Superficie aire (y=e): {T_p_final[:, -1].mean() - 273.15:.1f}°C")
    print(f"    Promedio: {T_p_final.mean() - 273.15:.1f}°C")
    print()
    
    print(f"  Aletas:")
    for k in range(3):
        T_a_k = T_a_final[k]
        print(f"    Aleta {k+1}: {T_a_k.mean() - 273.15:.1f}°C "
              f"[{T_a_k.min() - 273.15:.1f}, {T_a_k.max() - 273.15:.1f}]°C")
    print()
    
    # Balance energético final
    if len(resultados['metricas']['balance']) > 0:
        balance_final = resultados['metricas']['balance'][-1]
        print("⚡ Balance energético final:")
        print(f"  Q_in (agua):  {balance_final['Q_in']:.2f} W")
        print(f"  Q_out (aire): {balance_final['Q_out']:.2f} W")
        print(f"  dE/dt:        {balance_final['dE_dt']:.2f} W")
        print(f"  Error:        {balance_final['error_relativo']*100:.2f}%")
        print()
    
    print("=" * 70)
    print("🎉 Test completado exitosamente")
    print("=" * 70)
