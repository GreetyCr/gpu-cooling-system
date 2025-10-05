#!/usr/bin/env python3
"""
Interfaz Web para Simulador de Enfriamiento GPU
Usando Streamlit para visualización interactiva
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path
import time
import threading
import tempfile

# Configurar path
PROJECT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

from src.parametros import Parametros
from src.mallas import generar_todas_mallas
from src.solucionador import resolver_sistema

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Simulador GPU Cooling",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño profesional
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        color: black;
    }
    .status-running {
        color: #ff9800;
        font-weight: bold;
    }
    .status-complete {
        color: #4caf50;
        font-weight: bold;
    }
    .status-error {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<div class="main-header">🌡️ Simulador de Enfriamiento GPU</div>', 
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Transferencia de Calor con Aletas Cilíndricas</div>', 
            unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - CONFIGURACIÓN
# =============================================================================
st.sidebar.header("⚙️ Configuración")

# Material
material = st.sidebar.selectbox(
    "Material de la Placa",
    options=["Aluminio 6061", "Acero Inoxidable 304"],
    index=0,
    help="Selecciona el material del disipador"
)
material_code = "Al" if "Aluminio" in material else "SS"

# Tiempo de simulación
t_max = st.sidebar.slider(
    "Tiempo de Simulación (s)",
    min_value=5.0,
    max_value=60.0,
    value=30.0,
    step=5.0,
    help="Tiempo total de simulación física"
)

# Criterio de convergencia
epsilon = st.sidebar.select_slider(
    "Criterio de Convergencia (K/s)",
    options=[1e-4, 5e-4, 1e-3, 5e-3, 1e-2],
    value=1e-3,
    format_func=lambda x: f"{x:.0e}",
    help="Máxima tasa de cambio de temperatura para considerar convergencia"
)

# Frecuencia de guardado
guardar_cada = st.sidebar.number_input(
    "Guardar cada N pasos",
    min_value=50,
    max_value=1000,
    value=200,
    step=50,
    help="Mayor valor = menos puntos guardados = ejecución más rápida"
)

# Balance energético
calcular_balance = st.sidebar.checkbox(
    "Calcular Balance Energético",
    value=True,
    help="Activar validación de conservación de energía (incrementa ~20% tiempo)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Info del Sistema")

# Crear params temporal solo para mostrar info (no ejecutar simulación aún)
try:
    params_info = Parametros(material=material_code)
    sidebar_info = f"""
    **Material**: {material}
    
    **Geometría**:
    - Placa: {params_info.L_x*1000:.0f} × {params_info.e_base*1000:.0f} mm
    - Aletas: R={params_info.r*1000:.1f} mm, θ=60°
    - Flujo agua: 80°C, 0.5 m/s
    
    **Discretización**:
    - Fluido: {params_info.Nx_fluido} nodos
    - Placa: {params_info.Nx_placa} × {params_info.Ny_placa} nodos
    - Aletas: 3 × ({params_info.Nr_aleta} × {params_info.Ntheta_aleta} nodos)
    
    **Total**: {params_info.Nx_fluido + params_info.Nx_placa*params_info.Ny_placa + 3*params_info.Nr_aleta*params_info.Ntheta_aleta:,} nodos
    """
except:
    sidebar_info = f"""
    **Material**: {material}
    
    Información del sistema se cargará al inicializar la simulación.
    """

st.sidebar.info(sidebar_info)

# =============================================================================
# MAIN PANEL
# =============================================================================

# Botón de inicio
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button(
        "🚀 INICIAR SIMULACIÓN",
        type="primary",
        use_container_width=True
    )

st.markdown("---")

# =============================================================================
# EJECUCIÓN DE SIMULACIÓN
# =============================================================================
if run_button:
    try:
        # Placeholder para actualizaciones
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        metrics_placeholder = st.empty()
        
        # Inicialización
        status_placeholder.markdown(
            '<p class="status-running">⏳ Inicializando parámetros y mallas...</p>',
            unsafe_allow_html=True
        )
        
        params = Parametros(material=material_code)
        mallas = generar_todas_mallas(params)
        
        time.sleep(0.5)  # Para que el usuario vea el mensaje
        
        status_placeholder.markdown(
            '<p class="status-running">🔥 Ejecutando simulación (esto puede tomar varios minutos)...</p>',
            unsafe_allow_html=True
        )
        
        # Estimación de tiempo
        n_pasos_max = int(t_max / params.dt)
        tiempo_estimado = n_pasos_max * 0.01  # ~0.01s por paso (estimación conservadora)
        
        metrics_placeholder.markdown(f"""
        <div class="metric-card">
        <strong>Pasos totales</strong>: {n_pasos_max:,}<br>
        <strong>Tiempo estimado</strong>: {tiempo_estimado/60:.1f} minutos<br>
        <strong>Material</strong>: {material}<br>
        <strong>dt placa</strong>: {params.dt*1000:.3f} ms
        </div>
        """, unsafe_allow_html=True)
        
        # EJECUTAR SIMULACIÓN CON PROGRESO EN TIEMPO REAL
        start_time = time.time()
        
        # Crear archivo temporal para progreso
        progress_file = tempfile.mktemp(suffix='.progress')
        resultados = [None]  # Lista para almacenar resultado del thread
        error_container = [None]  # Para capturar errores
        
        def run_simulation():
            try:
                result = resolver_sistema(
                    params=params,
                    mallas=mallas,
                    t_max=t_max,
                    epsilon=epsilon,
                    guardar_cada=guardar_cada,
                    calcular_balance=calcular_balance,
                    verbose=False,  # No imprimir en consola
                    progress_file=progress_file
                )
                resultados[0] = result
            except Exception as e:
                error_container[0] = e
        
        # Iniciar simulación en thread separado
        sim_thread = threading.Thread(target=run_simulation)
        sim_thread.start()
        
        # Monitorear progreso en tiempo real
        progress_placeholder = st.empty()
        last_update = time.time()
        
        while sim_thread.is_alive():
            try:
                if os.path.exists(progress_file):
                    with open(progress_file, 'r') as f:
                        line = f.read().strip()
                        if line:
                            parts = line.split('|')
                            t_sim = float(parts[0])
                            max_rate = float(parts[1])
                            T_f = float(parts[2])
                            T_p = float(parts[3])
                            T_a = float(parts[4])
                            progress_pct = float(parts[5])
                            
                            # Actualizar barra de progreso
                            progress_bar.progress(int(progress_pct))
                            
                            # Actualizar información
                            progress_placeholder.markdown(f"""
                            <div class="metric-card">
                            <strong>⏱️ Tiempo simulado:</strong> {t_sim:.2f} s / {t_max:.1f} s ({progress_pct:.1f}%)<br>
                            <strong>🔥 max|dT/dt|:</strong> {max_rate:.2e} K/s<br>
                            <strong>🌡️ Temperaturas:</strong> Fluido={T_f:.1f}°C | Placa={T_p:.1f}°C | Aletas={T_a:.1f}°C<br>
                            <strong>⏳ Tiempo transcurrido:</strong> {(time.time()-start_time)/60:.1f} min
                            </div>
                            """, unsafe_allow_html=True)
                            
                            last_update = time.time()
            except:
                pass
            
            # Actualizar cada 0.5 segundos
            time.sleep(0.5)
            
            # Si no hay actualización en 10 segundos, mostrar mensaje
            if time.time() - last_update > 10:
                progress_placeholder.warning("⏳ Inicializando simulación...")
        
        # Esperar a que termine el thread
        sim_thread.join()
        
        # Limpiar archivo temporal
        try:
            if os.path.exists(progress_file):
                os.remove(progress_file)
        except:
            pass
        
        # Verificar si hubo error
        if error_container[0] is not None:
            raise error_container[0]
        
        # Obtener resultados
        resultados = resultados[0]
        elapsed_time = time.time() - start_time
        
        # Limpiar placeholder de progreso
        progress_placeholder.empty()
        
        # Completado
        progress_bar.progress(100)
        status_placeholder.markdown(
            f'<p class="status-complete">✅ Simulación completada en {elapsed_time/60:.1f} minutos</p>',
            unsafe_allow_html=True
        )
        
        # =============================================================================
        # RESULTADOS
        # =============================================================================
        st.markdown("---")
        st.header("📊 Resultados")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Tiempo Simulado",
                f"{resultados['tiempo'][-1]:.1f} s"
            )
        
        with col2:
            st.metric(
                "Puntos Guardados",
                f"{len(resultados['tiempo'])}"
            )
        
        with col3:
            convergencia = "✅ SÍ" if resultados['convergencia']['alcanzada'] else "❌ NO"
            st.metric(
                "Convergencia",
                convergencia
            )
        
        with col4:
            T_final = resultados['T_placa'][-1].mean() - 273.15
            st.metric(
                "T Placa Final",
                f"{T_final:.1f} °C"
            )
        
        # Tabs para diferentes visualizaciones
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Evolución Temporal", 
            "🗺️ Campos de Temperatura", 
            "⚡ Balance Energético",
            "💾 Datos"
        ])
        
        # TAB 1: EVOLUCIÓN TEMPORAL
        with tab1:
            st.subheader("Evolución de Temperaturas Promedio")
            
            tiempo = resultados['tiempo']
            T_fluido = resultados['T_fluido']
            T_placa = resultados['T_placa']
            T_aletas = resultados['T_aletas']
            
            # Calcular promedios
            T_f_mean = np.array([T.mean() - 273.15 for T in T_fluido])
            T_p_mean = np.array([T.mean() - 273.15 for T in T_placa])
            T_a_mean = np.array([np.mean([Ta.mean() for Ta in Tas]) - 273.15 
                                 for Tas in T_aletas])
            
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(tiempo, T_f_mean, 'b-', label='Fluido', linewidth=2.5, alpha=0.8)
            ax1.plot(tiempo, T_p_mean, 'r-', label='Placa', linewidth=2.5, alpha=0.8)
            ax1.plot(tiempo, T_a_mean, 'g-', label='Aletas', linewidth=2.5, alpha=0.8)
            
            ax1.set_xlabel('Tiempo (s)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
            ax1.set_title('Evolución Térmica del Sistema', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11, loc='best')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_xlim(0, tiempo[-1])
            
            st.pyplot(fig1)
            
            # Detalles adicionales
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🌡️ Temperaturas Finales:**")
                st.write(f"- Fluido: {T_f_mean[-1]:.1f} °C")
                st.write(f"- Placa: {T_p_mean[-1]:.1f} °C")
                st.write(f"- Aletas: {T_a_mean[-1]:.1f} °C")
            
            with col2:
                st.markdown("**📈 Tasas de Cambio:**")
                if len(tiempo) > 1:
                    dT_f = (T_f_mean[-1] - T_f_mean[-2]) / (tiempo[-1] - tiempo[-2])
                    dT_p = (T_p_mean[-1] - T_p_mean[-2]) / (tiempo[-1] - tiempo[-2])
                    dT_a = (T_a_mean[-1] - T_a_mean[-2]) / (tiempo[-1] - tiempo[-2])
                    st.write(f"- dT_f/dt: {dT_f:.2e} K/s")
                    st.write(f"- dT_p/dt: {dT_p:.2e} K/s")
                    st.write(f"- dT_a/dt: {dT_a:.2e} K/s")
        
        # TAB 2: CAMPOS DE TEMPERATURA
        with tab2:
            st.subheader("Distribución Espacial de Temperatura")
            
            # Selector de tiempo
            time_idx = st.slider(
                "Selecciona instante de tiempo",
                min_value=0,
                max_value=len(tiempo)-1,
                value=len(tiempo)-1,
                format=f"t = %.2f s"
            )
            
            t_selected = tiempo[time_idx]
            T_p_selected = T_placa[time_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Placa en t = {t_selected:.2f} s**")
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                im = ax2.imshow(
                    T_p_selected.T - 273.15,
                    aspect='auto',
                    origin='lower',
                    cmap='hot',
                    extent=[0, params.L_x*1000, 0, params.e_base*1000]
                )
                cbar = plt.colorbar(im, ax=ax2, label='Temperatura (°C)')
                ax2.set_xlabel('x (mm)', fontweight='bold')
                ax2.set_ylabel('y (mm)', fontweight='bold')
                ax2.set_title('Campo de Temperatura - Placa', fontweight='bold')
                st.pyplot(fig2)
            
            with col2:
                st.markdown(f"**Perfil Longitudinal (y = {params.e_base*1000/2:.1f} mm)**")
                x_placa = np.linspace(0, params.L_x*1000, T_p_selected.shape[0])
                T_perfil = T_p_selected[:, T_p_selected.shape[1]//2] - 273.15
                
                fig3, ax3 = plt.subplots(figsize=(8, 5))
                ax3.plot(x_placa, T_perfil, 'r-', linewidth=2.5)
                ax3.set_xlabel('Posición x (mm)', fontweight='bold')
                ax3.set_ylabel('Temperatura (°C)', fontweight='bold')
                ax3.set_title('Perfil de Temperatura - Centro Placa', fontweight='bold')
                ax3.grid(True, alpha=0.3, linestyle='--')
                st.pyplot(fig3)
        
        # TAB 3: BALANCE ENERGÉTICO
        with tab3:
            st.subheader("Balance Energético del Sistema")
            
            if calcular_balance and resultados['metricas']['balance']:
                balance = resultados['metricas']['balance']
                t_balance = np.array([b['tiempo'] for b in balance])
                Q_in = np.array([b['Q_in'] for b in balance])
                Q_out = np.array([b['Q_out'] for b in balance])
                dE_dt = np.array([b['dE_dt'] for b in balance])
                error_rel = np.array([b['error_relativo'] * 100 for b in balance])
                
                fig4, (ax4a, ax4b) = plt.subplots(2, 1, figsize=(12, 8))
                
                # Potencias
                ax4a.plot(t_balance, Q_in, 'b-', label='Q_in (entrada)', linewidth=2)
                ax4a.plot(t_balance, Q_out, 'r-', label='Q_out (salida)', linewidth=2)
                ax4a.plot(t_balance, dE_dt, 'g--', label='dE/dt (acumulación)', linewidth=2)
                ax4a.set_xlabel('Tiempo (s)', fontweight='bold')
                ax4a.set_ylabel('Potencia (W)', fontweight='bold')
                ax4a.set_title('Balance de Potencia', fontweight='bold')
                ax4a.legend(loc='best')
                ax4a.grid(True, alpha=0.3)
                
                # Error relativo
                ax4b.plot(t_balance, error_rel, 'k-', linewidth=2)
                ax4b.axhline(10, color='orange', linestyle='--', label='10% (aceptable)')
                ax4b.axhline(40, color='red', linestyle='--', label='40% (límite)')
                ax4b.set_xlabel('Tiempo (s)', fontweight='bold')
                ax4b.set_ylabel('Error Relativo (%)', fontweight='bold')
                ax4b.set_title('Error del Balance Energético', fontweight='bold')
                ax4b.legend(loc='best')
                ax4b.grid(True, alpha=0.3)
                ax4b.set_ylim(0, max(50, error_rel.max()*1.1))
                
                plt.tight_layout()
                st.pyplot(fig4)
                
                # Estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Q_in Inicial", f"{Q_in[0]:.1f} W")
                with col2:
                    st.metric("Q_in Final", f"{Q_in[-1]:.1f} W")
                with col3:
                    st.metric("Error Final", f"{error_rel[-1]:.1f} %")
            
            else:
                st.info("Balance energético no calculado. Activa la opción en la configuración.")
        
        # TAB 4: DATOS
        with tab4:
            st.subheader("Descarga de Resultados")
            
            st.markdown("""
            Los resultados se guardan automáticamente en:
            
            ```
            resultados/datos/resultados_{material}.npz
            ```
            
            El archivo contiene:
            - `tiempo`: Vector de tiempos
            - `T_fluido`: Lista de arrays de temperatura del fluido
            - `T_placa`: Lista de arrays 2D de temperatura de la placa
            - `T_aletas`: Lista de listas de arrays 2D de temperatura de aletas
            - `convergencia`: Diccionario con info de convergencia
            - `metricas`: Diccionario con balance energético
            """)
            
            # Información del archivo guardado
            ruta_resultados = PROJECT_DIR / "resultados" / "datos" / f"resultados_{material_code}.npz"
            
            if ruta_resultados.exists():
                tamaño = ruta_resultados.stat().st_size / (1024**2)  # MB
                st.success(f"✅ Archivo guardado: {ruta_resultados.name} ({tamaño:.2f} MB)")
                
                # Botón de descarga (simulado)
                st.download_button(
                    label="📥 Descargar Resultados (.npz)",
                    data=open(ruta_resultados, 'rb').read(),
                    file_name=ruta_resultados.name,
                    mime='application/octet-stream'
                )
                
                # Código para cargar
                st.markdown("**Código para cargar en Python:**")
                st.code(f"""
import numpy as np

data = np.load('resultados_{material_code}.npz', allow_pickle=True)
tiempo = data['tiempo']
T_fluido = data['T_fluido']
T_placa = data['T_placa']
T_aletas = data['T_aletas']
convergencia = data['convergencia'].item()
metricas = data['metricas'].item()
                """, language='python')
            
            else:
                st.warning("⚠️ Archivo de resultados no encontrado.")
    
    except Exception as e:
        status_placeholder.markdown(
            f'<p class="status-error">❌ Error durante la simulación</p>',
            unsafe_allow_html=True
        )
        st.error(f"Error: {str(e)}")
        st.exception(e)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem 0;">
    <p><strong>Sistema de Enfriamiento GPU con Aletas Cilíndricas</strong></p>
    <p>Simulación de Transferencia de Calor Multi-dominio</p>
    <p>Versión 1.0 | Octubre 2025</p>
</div>
""", unsafe_allow_html=True)
