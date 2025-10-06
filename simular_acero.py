#!/usr/bin/env python3
"""
Script: Simular Acero Inoxidable
=================================

Ejecuta simulación para acero inoxidable (SS) de 60 segundos.

Uso:
    python3 simular_acero.py
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.parametros import Parametros
from src.mallas import generar_todas_mallas
from src.solucionador import resolver_sistema

print("=" * 70)
print("SIMULACIÓN: ACERO INOXIDABLE (SS)")
print("=" * 70)

# Configurar parámetros para SS
print("\n1. Configurando parámetros...")
params = Parametros(material='SS')
print(f"   Material: Acero Inoxidable (SS)")
print(f"   k = {params.k_s} W/(m·K)")
print(f"   α = {params.alpha_s:.2e} m²/s")

# Generar mallas
print("\n2. Generando mallas...")
mallas = generar_todas_mallas(params)
print("   ✅ Mallas generadas")

# Ejecutar simulación
print("\n3. Ejecutando simulación (60s)...")
print("   ⏱️  Esto tomará ~10-15 minutos (SS es más lento que Al)...")
print()

resultados = resolver_sistema(
    params=params,
    mallas=mallas,
    t_max=60.0,
    epsilon=1e-3,
    guardar_cada=200,
    calcular_balance=True,
    verbose=True
)

print("\n" + "=" * 70)
print("✅ SIMULACIÓN COMPLETADA")
print("=" * 70)

# Temperaturas finales
T_f = resultados['T_fluido'][-1].mean() - 273.15
T_p = resultados['T_placa'][-1].mean() - 273.15
T_a = sum([T.mean() for T in resultados['T_aletas'][-1]])/3 - 273.15

print(f"\n🌡️  Temperaturas finales (t=60s):")
print(f"   Fluido: {T_f:.1f} °C")
print(f"   Placa:  {T_p:.1f} °C")
print(f"   Aletas: {T_a:.1f} °C")

if resultados['convergencia']['alcanzada']:
    print(f"\n✅ Convergencia alcanzada en t={resultados['convergencia']['t_convergencia']:.1f}s")
else:
    print(f"\n⚠️  Convergencia no alcanzada en 60s")

print(f"\n📁 Resultados guardados en:")
print(f"   resultados/datos/resultados_Stainless_Steel.npz")
print()
