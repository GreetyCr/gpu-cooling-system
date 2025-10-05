#!/usr/bin/env python3
"""
Script Principal: Sistema de Enfriamiento GPU
==============================================

Script maestro para ejecutar simulaciones térmicas del sistema de enfriamiento
de GPU con placa base y aletas cilíndricas.

Características:
    - Simulación térmica transitoria completa
    - Generación automática de visualizaciones
    - Comparación entre materiales (Al vs SS)
    - Modos: CLI, interactivo, o batch
    - Validación de prerequisitos
    - Manejo robusto de errores

Uso:
    # Modo por defecto (menú interactivo)
    python3 main.py
    
    # Simulación rápida + visualizaciones
    python3 main.py --rapido
    
    # Simulación completa hasta convergencia
    python3 main.py --completo
    
    # Solo visualizaciones de datos existentes
    python3 main.py --solo-visualizacion
    
    # Comparar materiales
    python3 main.py --comparar
    
    # Configuración personalizada
    python3 main.py --material SS --tiempo 120 --epsilon 5e-3
    
    # Ver ayuda completa
    python3 main.py --help

Autor: Sistema de Simulación Térmica
Fecha: Octubre 2025
Versión: 1.0.0
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import time

# ============================================================================
# CONFIGURACIÓN DE PATHS Y PREREQUISITOS
# ============================================================================

PROJECT_DIR = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_DIR / "src"
RESULTADOS_DIR = PROJECT_DIR / "resultados"
DATOS_DIR = RESULTADOS_DIR / "datos"
FIGURAS_DIR = RESULTADOS_DIR / "figuras"

# Agregar src al path
sys.path.insert(0, str(PROJECT_DIR))

# ============================================================================
# COLORES PARA TERMINAL
# ============================================================================

class Colors:
    """Códigos ANSI para colores en terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text: str, color: str = Colors.ENDC, bold: bool = False):
    """Imprime texto con color."""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.ENDC}")

def print_header(text: str):
    """Imprime header decorado."""
    print("\n" + "=" * 70)
    print_color(text.center(70), Colors.HEADER, bold=True)
    print("=" * 70 + "\n")

def print_section(text: str):
    """Imprime sección."""
    print()
    print_color(f"{'─' * 70}", Colors.OKBLUE)
    print_color(f"  {text}", Colors.OKBLUE, bold=True)
    print_color(f"{'─' * 70}", Colors.OKBLUE)

def print_success(text: str):
    """Imprime mensaje de éxito."""
    print_color(f"  ✅ {text}", Colors.OKGREEN)

def print_error(text: str):
    """Imprime mensaje de error."""
    print_color(f"  ❌ {text}", Colors.FAIL)

def print_warning(text: str):
    """Imprime mensaje de advertencia."""
    print_color(f"  ⚠️  {text}", Colors.WARNING)

def print_info(text: str):
    """Imprime mensaje informativo."""
    print_color(f"  ℹ️  {text}", Colors.OKCYAN)

# ============================================================================
# VALIDACIÓN DE PREREQUISITOS
# ============================================================================

def validar_prerequisitos() -> bool:
    """
    Valida que todos los prerequisitos estén instalados y disponibles.
    
    Returns:
        bool: True si todos los prerequisitos están OK, False en caso contrario
    """
    print_section("VALIDACIÓN DE PREREQUISITOS")
    
    todo_ok = True
    
    # 1. Verificar módulos de Python
    print_info("Verificando módulos de Python...")
    
    modulos_requeridos = [
        ('numpy', 'NumPy'),
        ('matplotlib', 'Matplotlib'),
        ('scipy', 'SciPy')
    ]
    
    for modulo, nombre in modulos_requeridos:
        try:
            __import__(modulo)
            print_success(f"{nombre} instalado")
        except ImportError:
            print_error(f"{nombre} NO encontrado")
            print_warning(f"   Instalar con: pip install {modulo}")
            todo_ok = False
    
    # 2. Verificar módulos del proyecto
    print()
    print_info("Verificando módulos del proyecto...")
    
    modulos_proyecto = [
        'parametros',
        'mallas',
        'fluido',
        'placa',
        'aletas',
        'acoplamiento',
        'solucionador',
        'visualizacion'
    ]
    
    for modulo in modulos_proyecto:
        archivo = SRC_DIR / f"{modulo}.py"
        if archivo.exists():
            print_success(f"src/{modulo}.py encontrado")
        else:
            print_error(f"src/{modulo}.py NO encontrado")
            todo_ok = False
    
    # 3. Verificar/crear directorios
    print()
    print_info("Verificando estructura de directorios...")
    
    for directorio in [RESULTADOS_DIR, DATOS_DIR, FIGURAS_DIR]:
        if directorio.exists():
            print_success(f"{directorio.relative_to(PROJECT_DIR)}/ existe")
        else:
            try:
                directorio.mkdir(parents=True, exist_ok=True)
                print_success(f"{directorio.relative_to(PROJECT_DIR)}/ creado")
            except Exception as e:
                print_error(f"Error creando {directorio}: {e}")
                todo_ok = False
    
    print()
    if todo_ok:
        print_success("Todos los prerequisitos OK")
    else:
        print_error("Algunos prerequisitos faltan")
    
    return todo_ok

# ============================================================================
# FUNCIONES DE SIMULACIÓN
# ============================================================================

def ejecutar_simulacion(
    material: str = 'Al',
    t_max: float = 30.0,
    epsilon: float = 1e-3,
    calcular_balance: bool = True,
    verbose: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una simulación térmica completa.
    
    Args:
        material: Material de la placa/aletas ('Al' o 'SS')
        t_max: Tiempo máximo de simulación [s]
        epsilon: Criterio de convergencia [K/s]
        calcular_balance: Si calcular balance energético
        verbose: Si mostrar progreso detallado
    
    Returns:
        Diccionario con resultados, o None si hubo error
    """
    print_section(f"EJECUTANDO SIMULACIÓN - Material: {material}")
    
    try:
        # Importar módulos necesarios
        from src.parametros import Parametros
        from src.mallas import generar_todas_mallas
        from src.solucionador import resolver_sistema
        
        # Configurar parámetros
        print_info("Configurando parámetros...")
        params = Parametros(material=material)
        
        print(f"     Material: {params.material_nombre}")
        print(f"     Conductividad: {params.k_s:.1f} W/(m·K)")
        print(f"     Difusividad: {params.alpha_s:.2e} m²/s")
        print(f"     Tiempo máximo: {t_max:.1f} s")
        print(f"     Criterio convergencia: {epsilon:.1e} K/s")
        
        # Generar mallas
        print()
        print_info("Generando mallas...")
        mallas = generar_todas_mallas(params)
        print_success("Mallas generadas")
        
        # Ejecutar simulación
        print()
        print_info(f"Iniciando simulación térmica...")
        print_warning("Esto puede tardar varios minutos...")
        print()
        
        t_inicio = time.time()
        
        resultados = resolver_sistema(
            params=params,
            mallas=mallas,
            t_max=t_max,
            epsilon=epsilon,
            guardar_cada=200,
            calcular_balance=calcular_balance,
            verbose=verbose
        )
        
        t_fin = time.time()
        duracion = t_fin - t_inicio
        
        print()
        print_success(f"Simulación completada en {duracion/60:.2f} minutos")
        
        # Información de convergencia
        if resultados['convergencia']['alcanzada']:
            t_conv = resultados['convergencia']['t_convergencia']
            print_success(f"Convergencia alcanzada en t={t_conv:.2f}s")
        else:
            print_warning(f"Convergencia no alcanzada en {t_max:.1f}s")
        
        # Temperaturas finales
        T_f_final = resultados['T_fluido'][-1].mean() - 273.15
        T_p_final = resultados['T_placa'][-1].mean() - 273.15
        T_a_final = sum([T.mean() for T in resultados['T_aletas'][-1]])/3 - 273.15
        
        print()
        print_info(f"Temperaturas finales (t={resultados['tiempo'][-1]:.2f}s):")
        print(f"     Fluido: {T_f_final:.1f} °C")
        print(f"     Placa:  {T_p_final:.1f} °C")
        print(f"     Aletas: {T_a_final:.1f} °C")
        
        return resultados
        
    except Exception as e:
        print_error(f"Error en simulación: {e}")
        import traceback
        print()
        print(traceback.format_exc())
        return None

# ============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def generar_visualizaciones(
    archivo_resultados: str = "resultados_Aluminio.npz"
) -> bool:
    """
    Genera todas las visualizaciones desde un archivo de resultados.
    
    Args:
        archivo_resultados: Nombre del archivo .npz con resultados
    
    Returns:
        bool: True si generación exitosa, False si hubo error
    """
    print_section("GENERANDO VISUALIZACIONES")
    
    try:
        from src.visualizacion import generar_reporte_completo, cargar_resultados
        from src.parametros import Parametros
        from src.mallas import generar_todas_mallas
        
        # Cargar resultados
        print_info(f"Cargando resultados: {archivo_resultados}...")
        resultados = cargar_resultados(archivo_resultados)
        
        # Extraer material del archivo
        material = 'Al' if 'Aluminio' in archivo_resultados else 'SS'
        params = Parametros(material=material)
        mallas = generar_todas_mallas(params)
        
        print_success("Resultados cargados")
        print(f"     Puntos temporales: {len(resultados['tiempo'])}")
        print(f"     Tiempo final: {resultados['tiempo'][-1]:.2f} s")
        
        # Generar reporte completo
        print()
        print_info("Generando gráficos...")
        
        figuras = generar_reporte_completo(
            resultados=resultados,
            mallas=mallas,
            params=params,
            epsilon=1e-3,
            crear_animacion_gif=False  # Animaciones son lentas
        )
        
        print()
        print_success(f"Generadas {len(figuras)} figuras")
        print_info(f"Guardadas en: {FIGURAS_DIR.relative_to(PROJECT_DIR)}/")
        
        # Listar figuras generadas
        for nombre in figuras.keys():
            print(f"     ✓ {nombre}")
        
        return True
        
    except Exception as e:
        print_error(f"Error generando visualizaciones: {e}")
        import traceback
        print()
        print(traceback.format_exc())
        return False

# ============================================================================
# FUNCIÓN DE COMPARACIÓN DE MATERIALES
# ============================================================================

def comparar_materiales(
    t_max: float = 30.0,
    epsilon: float = 1e-3
) -> bool:
    """
    Ejecuta simulaciones para Al y SS y genera comparación.
    
    Args:
        t_max: Tiempo máximo de simulación [s]
        epsilon: Criterio de convergencia [K/s]
    
    Returns:
        bool: True si exitoso, False si hubo error
    """
    print_header("COMPARACIÓN DE MATERIALES: ALUMINIO vs ACERO INOXIDABLE")
    
    materiales = ['Al', 'SS']
    resultados_dict = {}
    
    for material in materiales:
        print()
        resultado = ejecutar_simulacion(
            material=material,
            t_max=t_max,
            epsilon=epsilon,
            calcular_balance=True,
            verbose=True
        )
        
        if resultado is None:
            print_error(f"Fallo en simulación de {material}")
            return False
        
        resultados_dict[material] = resultado
    
    # Generar visualizaciones comparativas
    print()
    print_section("GENERANDO GRÁFICOS COMPARATIVOS")
    
    try:
        from src.visualizacion import comparar_materiales as comparar_viz
        
        fig = comparar_viz(
            resultados_Al=resultados_dict['Al'],
            resultados_SS=resultados_dict['SS'],
            guardar=True,
            nombre_archivo="comparacion_materiales.png"
        )
        
        print_success("Gráfico comparativo generado")
        print_info(f"Guardado en: {FIGURAS_DIR.relative_to(PROJECT_DIR)}/comparacion_materiales.png")
        
        return True
        
    except Exception as e:
        print_error(f"Error en comparación: {e}")
        return False

# ============================================================================
# MENÚ INTERACTIVO
# ============================================================================

def menu_interactivo():
    """
    Muestra menú interactivo para el usuario.
    """
    print_header("SISTEMA DE ENFRIAMIENTO GPU - MENÚ PRINCIPAL")
    
    print_info("Selecciona una opción:")
    print()
    print("  1. Simulación rápida (5 segundos)")
    print("  2. Simulación estándar (30 segundos)")
    print("  3. Simulación completa (hasta convergencia, ~60s)")
    print("  4. Solo generar visualizaciones (de datos existentes)")
    print("  5. Comparar materiales (Al vs SS)")
    print("  6. Configuración personalizada")
    print("  7. Salir")
    print()
    
    while True:
        try:
            opcion = input(Colors.OKBLUE + "  Opción [1-7]: " + Colors.ENDC).strip()
            
            if opcion == '1':
                # Simulación rápida
                print()
                resultado = ejecutar_simulacion(material='Al', t_max=5.0, epsilon=1e-3)
                if resultado:
                    generar_visualizaciones(archivo_resultados="resultados_Aluminio.npz")
                break
                
            elif opcion == '2':
                # Simulación estándar
                print()
                resultado = ejecutar_simulacion(material='Al', t_max=30.0, epsilon=1e-3)
                if resultado:
                    generar_visualizaciones(archivo_resultados="resultados_Aluminio.npz")
                break
                
            elif opcion == '3':
                # Simulación completa
                print()
                resultado = ejecutar_simulacion(material='Al', t_max=60.0, epsilon=1e-3)
                if resultado:
                    generar_visualizaciones(archivo_resultados="resultados_Aluminio.npz")
                break
                
            elif opcion == '4':
                # Solo visualizaciones
                print()
                print_info("Archivos disponibles:")
                archivos = list(DATOS_DIR.glob("resultados_*.npz"))
                if not archivos:
                    print_warning("No hay archivos de resultados")
                    break
                
                for i, archivo in enumerate(archivos, 1):
                    print(f"     {i}. {archivo.name}")
                
                print()
                idx = input(Colors.OKBLUE + "  Selecciona archivo [1-" + 
                           f"{len(archivos)}]: " + Colors.ENDC).strip()
                try:
                    archivo_sel = archivos[int(idx)-1].name
                    generar_visualizaciones(archivo_resultados=archivo_sel)
                except (ValueError, IndexError):
                    print_error("Selección inválida")
                break
                
            elif opcion == '5':
                # Comparar materiales
                print()
                comparar_materiales(t_max=30.0, epsilon=1e-3)
                break
                
            elif opcion == '6':
                # Configuración personalizada
                print()
                print_info("Configuración personalizada:")
                
                material = input("  Material [Al/SS] (default: Al): ").strip() or 'Al'
                t_max_str = input("  Tiempo máximo [s] (default: 30): ").strip() or '30'
                epsilon_str = input("  Criterio convergencia [K/s] (default: 1e-3): ").strip() or '1e-3'
                
                try:
                    t_max = float(t_max_str)
                    epsilon = float(epsilon_str)
                    
                    print()
                    resultado = ejecutar_simulacion(
                        material=material,
                        t_max=t_max,
                        epsilon=epsilon
                    )
                    
                    if resultado:
                        generar_viz = input("\n  ¿Generar visualizaciones? [s/n]: ").strip().lower()
                        if generar_viz == 's':
                            archivo = f"resultados_{'Aluminio' if material=='Al' else 'Stainless_Steel'}.npz"
                            generar_visualizaciones(archivo_resultados=archivo)
                    
                except ValueError:
                    print_error("Valores inválidos")
                break
                
            elif opcion == '7':
                print()
                print_info("¡Hasta luego!")
                return
                
            else:
                print_error("Opción inválida, intenta de nuevo")
                
        except KeyboardInterrupt:
            print()
            print_info("Operación cancelada")
            return
        except EOFError:
            print()
            return

# ============================================================================
# PARSEO DE ARGUMENTOS CLI
# ============================================================================

def parse_argumentos():
    """
    Parsea argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Sistema de Enfriamiento GPU - Simulación Térmica',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  Menú interactivo (por defecto):
    python3 main.py
  
  Simulación rápida con visualizaciones:
    python3 main.py --rapido
  
  Simulación completa hasta convergencia:
    python3 main.py --completo
  
  Solo generar visualizaciones:
    python3 main.py --solo-visualizacion
  
  Comparar materiales:
    python3 main.py --comparar
  
  Configuración personalizada:
    python3 main.py --material SS --tiempo 120 --epsilon 5e-3
  
  Sin validación de prerequisitos (más rápido):
    python3 main.py --sin-validacion --rapido

Para más información: https://github.com/tu-repo/python-adrian
        """
    )
    
    # Modos de ejecución
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument(
        '--rapido',
        action='store_true',
        help='Simulación rápida (5s) + visualizaciones'
    )
    modos.add_argument(
        '--completo',
        action='store_true',
        help='Simulación completa hasta convergencia (60s) + visualizaciones'
    )
    modos.add_argument(
        '--solo-visualizacion',
        action='store_true',
        help='Solo generar visualizaciones de datos existentes'
    )
    modos.add_argument(
        '--comparar',
        action='store_true',
        help='Comparar materiales (Al vs SS)'
    )
    modos.add_argument(
        '--interactivo',
        action='store_true',
        help='Modo interactivo con menú'
    )
    
    # Parámetros de simulación
    parser.add_argument(
        '--material',
        type=str,
        choices=['Al', 'SS'],
        default='Al',
        help='Material de la placa/aletas (default: Al)'
    )
    parser.add_argument(
        '--tiempo',
        type=float,
        default=30.0,
        metavar='T',
        help='Tiempo máximo de simulación en segundos (default: 30)'
    )
    parser.add_argument(
        '--epsilon',
        type=float,
        default=1e-3,
        metavar='E',
        help='Criterio de convergencia en K/s (default: 1e-3)'
    )
    
    # Opciones de visualización
    parser.add_argument(
        '--sin-graficos',
        action='store_true',
        help='No generar visualizaciones automáticamente'
    )
    parser.add_argument(
        '--archivo-resultados',
        type=str,
        default='resultados_Aluminio.npz',
        metavar='FILE',
        help='Archivo de resultados para visualización (default: resultados_Aluminio.npz)'
    )
    
    # Opciones generales
    parser.add_argument(
        '--sin-validacion',
        action='store_true',
        help='Saltar validación de prerequisitos'
    )
    parser.add_argument(
        '--silencioso',
        action='store_true',
        help='Modo silencioso (menos output)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Sistema de Enfriamiento GPU v1.0.0'
    )
    
    return parser.parse_args()

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal del script.
    """
    args = parse_argumentos()
    
    # Header
    if not args.silencioso:
        print_header("SISTEMA DE ENFRIAMIENTO GPU")
        print_info("Simulación Térmica Transitoria")
        print_info("Versión 1.0.0")
    
    # Validar prerequisitos (a menos que se salte)
    if not args.sin_validacion:
        if not validar_prerequisitos():
            print()
            print_error("Prerequisitos faltantes. Corrige los errores y vuelve a intentar.")
            print_info("O usa --sin-validacion para saltar esta verificación.")
            return 1
    
    # Determinar modo de ejecución
    try:
        # Modo interactivo (default si no hay otros argumentos)
        if args.interactivo or not any([
            args.rapido, args.completo, args.solo_visualizacion, args.comparar
        ]):
            menu_interactivo()
            
        # Modo rápido
        elif args.rapido:
            print()
            resultado = ejecutar_simulacion(
                material=args.material,
                t_max=5.0,
                epsilon=args.epsilon,
                verbose=not args.silencioso
            )
            if resultado and not args.sin_graficos:
                generar_visualizaciones(
                    archivo_resultados=f"resultados_{'Aluminio' if args.material=='Al' else 'Stainless_Steel'}.npz"
                )
        
        # Modo completo
        elif args.completo:
            print()
            resultado = ejecutar_simulacion(
                material=args.material,
                t_max=60.0,
                epsilon=args.epsilon,
                verbose=not args.silencioso
            )
            if resultado and not args.sin_graficos:
                generar_visualizaciones(
                    archivo_resultados=f"resultados_{'Aluminio' if args.material=='Al' else 'Stainless_Steel'}.npz"
                )
        
        # Solo visualización
        elif args.solo_visualizacion:
            print()
            generar_visualizaciones(archivo_resultados=args.archivo_resultados)
        
        # Comparación
        elif args.comparar:
            print()
            comparar_materiales(t_max=args.tiempo, epsilon=args.epsilon)
        
        # Modo personalizado (con parámetros pero sin flags de modo)
        else:
            print()
            resultado = ejecutar_simulacion(
                material=args.material,
                t_max=args.tiempo,
                epsilon=args.epsilon,
                verbose=not args.silencioso
            )
            if resultado and not args.sin_graficos:
                generar_visualizaciones(
                    archivo_resultados=f"resultados_{'Aluminio' if args.material=='Al' else 'Stainless_Steel'}.npz"
                )
        
        # Mensaje final
        if not args.silencioso:
            print()
            print_header("PROCESO COMPLETADO")
            print_success("Todos los resultados guardados en: resultados/")
            print_info(f"Datos: {DATOS_DIR.relative_to(PROJECT_DIR)}/")
            print_info(f"Figuras: {FIGURAS_DIR.relative_to(PROJECT_DIR)}/")
            print()
        
        return 0
        
    except KeyboardInterrupt:
        print()
        print_warning("Operación cancelada por el usuario")
        return 130
        
    except Exception as e:
        print()
        print_error(f"Error inesperado: {e}")
        import traceback
        print()
        print(traceback.format_exc())
        return 1

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())
