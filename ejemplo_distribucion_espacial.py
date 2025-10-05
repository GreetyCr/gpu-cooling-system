#!/usr/bin/env python3
"""
Script de Ejemplo: Distribución Espacial de Temperatura
========================================================

Este script genera un gráfico especial que muestra la distribución
espacial completa del sistema de enfriamiento GPU:

- Placa base con perfil de temperatura
- 3 aletas cilíndricas en sus posiciones reales
- Zona de agua fluyendo entre las aletas
- Perfiles de temperatura en cortes verticales

Uso:
    python3 ejemplo_distribucion_espacial.py

Autor: Sistema de Simulación
Fecha: Octubre 2025
"""

import sys
from pathlib import Path

# Agregar directorio del proyecto al path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.visualizacion import (
    graficar_distribucion_espacial_completa, 
    cargar_resultados
)
from src.parametros import Parametros
from src.mallas import generar_todas_mallas

def main():
    """
    Función principal para generar la distribución espacial.
    """
    print("=" * 70)
    print("DISTRIBUCIÓN ESPACIAL DE TEMPERATURA")
    print("Sistema de Enfriamiento GPU con Aletas Cilíndricas")
    print("=" * 70)
    
    # 1. Cargar resultados de la simulación
    print("\n1. Cargando resultados...")
    try:
        resultados = cargar_resultados("resultados_Aluminio.npz")
    except:
        print("   ⚠️ No se encontró resultados_Aluminio.npz")
        print("   ℹ️  Ejecuta primero una simulación con solucionador.py")
        return
    
    # 2. Cargar parámetros y mallas
    print("2. Inicializando parámetros y mallas...")
    params = Parametros(material='Al')
    mallas = generar_todas_mallas(params)
    
    # 3. Generar figura de distribución espacial
    print("3. Generando gráfico de distribución espacial...")
    print("   ℹ️  Este gráfico muestra:")
    print("      - Placa base con perfil de temperatura")
    print("      - 3 aletas en sus posiciones reales (5, 15, 25 mm)")
    print("      - Zona de agua entre aletas")
    print("      - Perfiles verticales de temperatura")
    
    fig = graficar_distribucion_espacial_completa(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=-1,  # Último instante temporal
        guardar=True,
        mostrar=False
    )
    
    print("\n" + "=" * 70)
    print("✅ GRÁFICO GENERADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📊 Figura guardada en:")
    print(f"   resultados/figuras/distribucion_espacial_{params.material}_t{resultados['tiempo'][-1]:.2f}s.png")
    print(f"\n📐 Geometría del sistema:")
    print(f"   - Longitud placa: {params.L_x*1000:.1f} mm")
    print(f"   - Espesor placa: {params.e_base*1000:.1f} mm")
    print(f"   - Radio aletas: {params.r*1000:.1f} mm")
    print(f"   - Posiciones aletas: {params.x_aleta_1*1000:.1f}, {params.x_aleta_2*1000:.1f}, {params.x_aleta_3*1000:.1f} mm")
    print(f"\n🌡️  Temperaturas finales:")
    print(f"   - Fluido: {(resultados['T_fluido'][-1].mean() - 273.15):.1f} °C")
    print(f"   - Placa: {(resultados['T_placa'][-1].mean() - 273.15):.1f} °C")
    print(f"   - Aletas: {(sum([T.mean() for T in resultados['T_aletas'][-1]])/3 - 273.15):.1f} °C")
    print()


if __name__ == "__main__":
    main()
