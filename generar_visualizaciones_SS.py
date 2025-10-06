#!/usr/bin/env python3
"""
Script: Generar TODAS las Visualizaciones para Acero Inoxidable (SS)
=====================================================================

Genera todas las figuras solicitadas para SS en t=5s y t=60s:
- Balance energético
- Evolución temporal
- Campos 2D (t=5 y t=60)
- Distribución espacial (t=5 y t=60)
- Perfiles espaciales (t=5 y t=60)
- Convergencia

Uso:
    python3 generar_visualizaciones_SS.py
    
Tiempo estimado: ~2-3 minutos
"""

import sys
from pathlib import Path
import numpy as np

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.visualizacion import (
    cargar_resultados,
    graficar_evolucion_temporal,
    graficar_perfiles_espaciales,
    graficar_campo_2d,
    graficar_balance_energetico,
    graficar_convergencia,
    graficar_distribucion_espacial_completa
)
from src.parametros import Parametros
from src.mallas import generar_todas_mallas

print("=" * 70)
print("GENERACIÓN DE VISUALIZACIONES - ACERO INOXIDABLE (SS)")
print("=" * 70)

# Cargar resultados
print("\n1. Cargando resultados de SS...")
try:
    resultados = cargar_resultados("resultados_AceroInox.npz")
    print("   ✅ Resultados cargados")
    print(f"   Puntos temporales: {len(resultados['tiempo'])}")
    print(f"   Tiempo final: {resultados['tiempo'][-1]:.2f} s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Asegúrate de que la simulación de SS haya completado.")
    sys.exit(1)

# Configurar parámetros y mallas
print("\n2. Configurando parámetros y mallas...")
params = Parametros(material='SS')
mallas = generar_todas_mallas(params)
print("   ✅ Configuración lista")

# Encontrar índices para t≈5s y t=60s
tiempo = resultados['tiempo']
idx_t5 = np.argmin(np.abs(tiempo - 5.0))
idx_t60 = np.argmin(np.abs(tiempo - 60.0))

t5_real = tiempo[idx_t5]
t60_real = tiempo[idx_t60]

print(f"\n   Índices temporales:")
print(f"   - t≈5s: índice {idx_t5}, t={t5_real:.2f}s")
print(f"   - t≈60s: índice {idx_t60}, t={t60_real:.2f}s")

# Lista de figuras a generar
figuras_generadas = []

# ============================================================================
# 1. BALANCE ENERGÉTICO
# ============================================================================
print("\n" + "=" * 70)
print("3. Generando Balance Energético SS...")
print("=" * 70)

try:
    fig = graficar_balance_energetico(
        resultados=resultados,
        params=params,
        guardar=True,
        nombre_archivo="balance_energetico_SS.png",
        mostrar=False
    )
    print("   ✅ balance_energetico_SS.png")
    figuras_generadas.append("balance_energetico_SS.png")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# ============================================================================
# 2. EVOLUCIÓN TEMPORAL
# ============================================================================
print("\n" + "=" * 70)
print("4. Generando Evolución Temporal SS...")
print("=" * 70)

try:
    fig = graficar_evolucion_temporal(
        resultados=resultados,
        params=params,
        guardar=True,
        nombre_archivo="evolucion_temporal_SS.png",
        mostrar=False
    )
    print("   ✅ evolucion_temporal_SS.png")
    figuras_generadas.append("evolucion_temporal_SS.png")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# ============================================================================
# 3. CONVERGENCIA
# ============================================================================
print("\n" + "=" * 70)
print("5. Generando Convergencia SS...")
print("=" * 70)

try:
    fig = graficar_convergencia(
        resultados=resultados,
        params=params,
        epsilon=1e-3,
        guardar=True,
        nombre_archivo="convergencia_SS.png",
        mostrar=False
    )
    print("   ✅ convergencia_SS.png")
    figuras_generadas.append("convergencia_SS.png")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# ============================================================================
# 4. PERFILES ESPACIALES (t=5s y t=60s)
# ============================================================================
print("\n" + "=" * 70)
print("6. Generando Perfiles Espaciales SS...")
print("=" * 70)

# t ≈ 5s
try:
    fig = graficar_perfiles_espaciales(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t5,
        guardar=True,
        nombre_archivo=f"perfiles_espaciales_SS_t{t5_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ perfiles_espaciales_SS_t{t5_real:.2f}s.png")
    figuras_generadas.append(f"perfiles_espaciales_SS_t{t5_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t5_real:.2f}s: {e}")

# t ≈ 60s
try:
    fig = graficar_perfiles_espaciales(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t60,
        guardar=True,
        nombre_archivo=f"perfiles_espaciales_SS_t{t60_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ perfiles_espaciales_SS_t{t60_real:.2f}s.png")
    figuras_generadas.append(f"perfiles_espaciales_SS_t{t60_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t60_real:.2f}s: {e}")

# ============================================================================
# 5. CAMPOS 2D (t=5s y t=60s)
# ============================================================================
print("\n" + "=" * 70)
print("7. Generando Campos 2D SS...")
print("=" * 70)

# t ≈ 5s
try:
    fig = graficar_campo_2d(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t5,
        guardar=True,
        nombre_archivo=f"campos_2d_SS_t{t5_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ campos_2d_SS_t{t5_real:.2f}s.png")
    figuras_generadas.append(f"campos_2d_SS_t{t5_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t5_real:.2f}s: {e}")

# t ≈ 60s
try:
    fig = graficar_campo_2d(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t60,
        guardar=True,
        nombre_archivo=f"campos_2d_SS_t{t60_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ campos_2d_SS_t{t60_real:.2f}s.png")
    figuras_generadas.append(f"campos_2d_SS_t{t60_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t60_real:.2f}s: {e}")

# ============================================================================
# 6. DISTRIBUCIÓN ESPACIAL COMPLETA (t=5s y t=60s)
# ============================================================================
print("\n" + "=" * 70)
print("8. Generando Distribución Espacial Completa SS...")
print("=" * 70)

# t ≈ 5s
try:
    fig = graficar_distribucion_espacial_completa(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t5,
        guardar=True,
        nombre_archivo=f"distribucion_espacial_SS_t{t5_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ distribucion_espacial_SS_t{t5_real:.2f}s.png")
    figuras_generadas.append(f"distribucion_espacial_SS_t{t5_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t5_real:.2f}s: {e}")

# t ≈ 60s
try:
    fig = graficar_distribucion_espacial_completa(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_t60,
        guardar=True,
        nombre_archivo=f"distribucion_espacial_SS_t{t60_real:.2f}s.png",
        mostrar=False
    )
    print(f"   ✅ distribucion_espacial_SS_t{t60_real:.2f}s.png")
    figuras_generadas.append(f"distribucion_espacial_SS_t{t60_real:.2f}s.png")
except Exception as e:
    print(f"   ⚠️  Error en t={t60_real:.2f}s: {e}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 70)
print("✅ GENERACIÓN COMPLETADA")
print("=" * 70)

print(f"\n📊 Figuras generadas: {len(figuras_generadas)}/11")
print(f"\n📁 Ubicación: resultados/figuras/")
print("\nLista de figuras:")
for i, fig in enumerate(figuras_generadas, 1):
    print(f"   {i:2d}. {fig}")

# Temperaturas finales
T_f_5 = resultados['T_fluido'][idx_t5].mean() - 273.15
T_p_5 = resultados['T_placa'][idx_t5].mean() - 273.15
T_a_5 = sum([T.mean() for T in resultados['T_aletas'][idx_t5]])/3 - 273.15

T_f_60 = resultados['T_fluido'][idx_t60].mean() - 273.15
T_p_60 = resultados['T_placa'][idx_t60].mean() - 273.15
T_a_60 = sum([T.mean() for T in resultados['T_aletas'][idx_t60]])/3 - 273.15

print(f"\n🌡️  Temperaturas SS:")
print(f"\n   t={t5_real:.2f}s:")
print(f"   - Fluido: {T_f_5:.1f} °C")
print(f"   - Placa:  {T_p_5:.1f} °C")
print(f"   - Aletas: {T_a_5:.1f} °C")

print(f"\n   t={t60_real:.2f}s:")
print(f"   - Fluido: {T_f_60:.1f} °C")
print(f"   - Placa:  {T_p_60:.1f} °C")
print(f"   - Aletas: {T_a_60:.1f} °C")

print(f"\n   Δ (t=60s - t=5s):")
print(f"   - Fluido: {T_f_60 - T_f_5:+.1f} °C")
print(f"   - Placa:  {T_p_60 - T_p_5:+.1f} °C")
print(f"   - Aletas: {T_a_60 - T_a_5:+.1f} °C")

print("\n🎯 Ahora tienes todas las visualizaciones de SS para comparar con Al!")
print()
