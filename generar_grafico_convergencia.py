#!/usr/bin/env python3
"""
Script: Gráfico de Distribución Espacial en Convergencia
=========================================================

Este script:
1. Ejecuta una simulación hasta alcanzar estado estacionario
2. Genera el gráfico de distribución espacial en el instante de convergencia
3. Compara con el gráfico al tiempo final

Uso:
    python3 generar_grafico_convergencia.py

Autor: Sistema de Simulación
Fecha: Octubre 2025
"""

import sys
from pathlib import Path
import numpy as np

# Agregar directorio del proyecto al path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.parametros import Parametros
from src.mallas import generar_todas_mallas
from src.solucionador import resolver_sistema
from src.visualizacion import (
    graficar_distribucion_espacial_completa,
    cargar_resultados
)

def main():
    """
    Función principal para generar gráfico en convergencia.
    """
    print("=" * 70)
    print("GRÁFICO DE DISTRIBUCIÓN ESPACIAL EN CONVERGENCIA")
    print("Sistema de Enfriamiento GPU")
    print("=" * 70)
    
    # Verificar si ya existe una simulación con convergencia
    archivo_resultados = PROJECT_DIR / "resultados" / "datos" / "resultados_Aluminio.npz"
    
    ejecutar_simulacion = True
    
    if archivo_resultados.exists():
        print("\n1. Verificando resultados existentes...")
        data = np.load(archivo_resultados, allow_pickle=True)
        
        if 'convergencia_alcanzada' in data.files:
            convergencia = bool(data['convergencia_alcanzada'])
            
            if convergencia:
                t_conv = float(data['t_convergencia'])
                print(f"   ✅ Convergencia ya alcanzada en t={t_conv:.2f}s")
                ejecutar_simulacion = False
            else:
                print("   ⚠️ Simulación previa no alcanzó convergencia")
                print("   📝 Tiempo máximo previo:", data['tiempo'][-1], "s")
                ejecutar_simulacion = True
        else:
            print("   ⚠️ Datos previos sin información de convergencia")
            ejecutar_simulacion = True
    
    # Ejecutar simulación si es necesario
    if ejecutar_simulacion:
        print("\n2. Ejecutando nueva simulación hasta convergencia...")
        print("   ⏱️  Esto puede tardar varios minutos...")
        print()
        
        # Configurar parámetros
        params = Parametros(material='Al')
        mallas = generar_todas_mallas(params)
        
        # Ejecutar simulación
        # Tiempo máximo amplio para asegurar convergencia
        t_max = 60.0  # 60 segundos
        epsilon = 1e-3  # Criterio de convergencia
        
        print(f"   Configuración:")
        print(f"   - Material: Aluminio")
        print(f"   - t_max: {t_max} s")
        print(f"   - epsilon: {epsilon:.1e} K/s")
        print(f"   - Guardando cada 200 pasos")
        print()
        
        resultados = resolver_sistema(
            params=params,
            mallas=mallas,
            t_max=t_max,
            epsilon=epsilon,
            guardar_cada=200,
            calcular_balance=True,
            verbose=True
        )
        
        print(f"\n   ✅ Simulación completada")
        
        # Verificar convergencia
        if resultados['convergencia']['alcanzada']:
            t_conv = resultados['convergencia']['t_convergencia']
            print(f"   ✅ Convergencia alcanzada en t={t_conv:.2f}s")
        else:
            print(f"   ⚠️ No se alcanzó convergencia en {t_max}s")
            print(f"   ℹ️  Se generará gráfico al tiempo final")
    else:
        # Cargar resultados existentes
        print("\n2. Cargando resultados existentes...")
        resultados = cargar_resultados("resultados_Aluminio.npz")
        params = Parametros(material='Al')
        mallas = generar_todas_mallas(params)
    
    # Encontrar índice de convergencia
    print("\n3. Identificando instante de convergencia...")
    
    if resultados['convergencia']['alcanzada']:
        t_conv = resultados['convergencia']['t_convergencia']
        tiempo = resultados['tiempo']
        
        # Encontrar índice más cercano al tiempo de convergencia
        idx_conv = np.argmin(np.abs(tiempo - t_conv))
        t_real = tiempo[idx_conv]
        
        print(f"   Tiempo de convergencia: {t_conv:.2f} s")
        print(f"   Índice correspondiente: {idx_conv}")
        print(f"   Tiempo real del índice: {t_real:.2f} s")
    else:
        # Usar último índice si no hay convergencia
        idx_conv = -1
        t_real = resultados['tiempo'][-1]
        print(f"   ⚠️ Convergencia no alcanzada")
        print(f"   Usando tiempo final: {t_real:.2f} s")
    
    # Generar gráfico en convergencia
    print("\n4. Generando gráfico de distribución espacial...")
    
    fig = graficar_distribucion_espacial_completa(
        resultados=resultados,
        mallas=mallas,
        params=params,
        tiempo_idx=idx_conv,
        guardar=True,
        nombre_archivo=f"distribucion_espacial_convergencia_Al_t{t_real:.2f}s.png",
        mostrar=False
    )
    
    # También generar gráfico al tiempo final para comparación
    if idx_conv != -1:
        print("\n5. Generando gráfico al tiempo final para comparación...")
        
        fig_final = graficar_distribucion_espacial_completa(
            resultados=resultados,
            mallas=mallas,
            params=params,
            tiempo_idx=-1,
            guardar=True,
            nombre_archivo=f"distribucion_espacial_final_Al_t{resultados['tiempo'][-1]:.2f}s.png",
            mostrar=False
        )
    
    # Resumen
    print("\n" + "=" * 70)
    print("✅ GRÁFICOS GENERADOS EXITOSAMENTE")
    print("=" * 70)
    
    print(f"\n📊 Figuras guardadas:")
    print(f"   1. resultados/figuras/distribucion_espacial_convergencia_Al_t{t_real:.2f}s.png")
    if idx_conv != -1:
        print(f"   2. resultados/figuras/distribucion_espacial_final_Al_t{resultados['tiempo'][-1]:.2f}s.png")
    
    print(f"\n🌡️  Temperaturas en convergencia (t={t_real:.2f}s):")
    T_f_conv = resultados['T_fluido'][idx_conv].mean() - 273.15
    T_p_conv = resultados['T_placa'][idx_conv].mean() - 273.15
    T_a_conv = sum([T.mean() for T in resultados['T_aletas'][idx_conv]])/3 - 273.15
    print(f"   - Fluido: {T_f_conv:.1f} °C")
    print(f"   - Placa: {T_p_conv:.1f} °C")
    print(f"   - Aletas: {T_a_conv:.1f} °C")
    
    if idx_conv != -1:
        print(f"\n🌡️  Temperaturas al tiempo final (t={resultados['tiempo'][-1]:.2f}s):")
        T_f_final = resultados['T_fluido'][-1].mean() - 273.15
        T_p_final = resultados['T_placa'][-1].mean() - 273.15
        T_a_final = sum([T.mean() for T in resultados['T_aletas'][-1]])/3 - 273.15
        print(f"   - Fluido: {T_f_final:.1f} °C")
        print(f"   - Placa: {T_p_final:.1f} °C")
        print(f"   - Aletas: {T_a_final:.1f} °C")
        
        print(f"\n📈 Cambio después de convergencia:")
        print(f"   - Fluido: {abs(T_f_final - T_f_conv):.2f} °C")
        print(f"   - Placa: {abs(T_p_final - T_p_conv):.2f} °C")
        print(f"   - Aletas: {abs(T_a_final - T_a_conv):.2f} °C")
    
    print()


if __name__ == "__main__":
    main()
