#!/usr/bin/env python3
"""
Script Rápido: Gráfico de Distribución Espacial
================================================

Genera el gráfico de distribución espacial con los datos existentes.

Uso:
    python3 generar_grafico_rapido.py

Tiempo de ejecución: < 10 segundos
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.visualizacion import graficar_distribucion_espacial_completa, cargar_resultados
from src.parametros import Parametros
from src.mallas import generar_todas_mallas

print("=" * 70)
print("GRÁFICO RÁPIDO: Distribución Espacial")
print("=" * 70)

# Cargar resultados existentes
print("\n1. Cargando resultados...")
resultados = cargar_resultados("resultados_Aluminio.npz")
params = Parametros(material='Al')
mallas = generar_todas_mallas(params)

# Generar gráfico al tiempo final
print("2. Generando gráfico al tiempo final...")
tiempo_final = resultados['tiempo'][-1]

fig = graficar_distribucion_espacial_completa(
    resultados=resultados,
    mallas=mallas,
    params=params,
    tiempo_idx=-1,
    guardar=True,
    nombre_archivo=f"distribucion_espacial_rapido_Al_t{tiempo_final:.2f}s.png",
    mostrar=False
)

print("\n" + "=" * 70)
print("✅ GRÁFICO GENERADO")
print("=" * 70)
print(f"\n📊 Figura guardada:")
print(f"   resultados/figuras/distribucion_espacial_rapido_Al_t{tiempo_final:.2f}s.png")

T_f = resultados['T_fluido'][-1].mean() - 273.15
T_p = resultados['T_placa'][-1].mean() - 273.15
T_a = sum([T.mean() for T in resultados['T_aletas'][-1]])/3 - 273.15

print(f"\n🌡️  Temperaturas en t={tiempo_final:.2f}s:")
print(f"   - Fluido: {T_f:.1f} °C")
print(f"   - Placa: {T_p:.1f} °C")
print(f"   - Aletas: {T_a:.1f} °C")

print(f"\n⚠️  Nota: Este gráfico corresponde al tiempo final de la simulación")
print(f"   disponible ({tiempo_final:.1f}s), no necesariamente el estado estacionario.")
print(f"\n💡 Para gráfico en convergencia, usa: generar_grafico_convergencia.py")
print()
