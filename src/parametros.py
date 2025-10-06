"""
Módulo de parámetros del sistema de enfriamiento GPU.

Este módulo contiene la clase Parametros que encapsula todos los parámetros
geométricos, operativos, termofísicos y numéricos necesarios para la simulación.

Referencias:
- Geometría: Tabla I en contexto/02_parametros_sistema.md
- Operación: Tabla II en contexto/02_parametros_sistema.md
- Propiedades: Tablas III, IV, V en contexto/02_parametros_sistema.md
- Discretización: contexto/05_discretizacion_numerica.md
"""

import numpy as np
from typing import Literal


class Parametros:
    """
    Clase que almacena todos los parámetros del sistema de enfriamiento GPU.
    
    Esta clase maneja los parámetros geométricos, operativos, propiedades
    termofísicas y parámetros numéricos para la simulación transitoria de
    transferencia de calor.
    
    Attributes:
        material (str): Material del sistema ('Al' para Aluminio 6061, 
                       'SS' para Acero Inoxidable 304)
        
    Parámetros Geométricos (Tabla I):
        L_x (float): Longitud en dirección del flujo [m]
        W (float): Ancho/profundidad en eje z [m]
        e_base (float): Espesor de la placa base [m]
        e_agua (float): Claro hidráulico del canal [m]
        D (float): Diámetro de los domos [m]
        r (float): Radio de los domos [m]
        p (float): Paso entre domos [m]
        s (float): Separación plana entre domos [m]
        N (int): Número de domos
        
    Parámetros Operativos (Tabla II):
        Q (float): Caudal de agua [m³/s]
        u (float): Velocidad media del agua [m/s]
        h_agua (float): Coeficiente convectivo agua-placa [W·m⁻²·K⁻¹]
        h_aire (float): Coeficiente convectivo aire-superficie [W·m⁻²·K⁻¹]
        T_inf (float): Temperatura del aire ambiente [K]
        T_inicial (float): Temperatura inicial del sólido [K]
        T_f_in_inicial (float): Temperatura entrada agua inicial [K]
        T_f_in (float): Temperatura entrada agua (nueva) [K]
        
    Propiedades del Agua (Tabla III):
        k_w (float): Conductividad térmica del agua [W·m⁻¹·K⁻¹]
        rho_agua (float): Densidad del agua [kg·m⁻³]
        cp_agua (float): Calor específico del agua [J·kg⁻¹·K⁻¹]
        
    Propiedades del Material (Tablas IV y V):
        k_s (float): Conductividad térmica del sólido [W·m⁻¹·K⁻¹]
        rho_s (float): Densidad del sólido [kg·m⁻³]
        cp_s (float): Calor específico del sólido [J·kg⁻¹·K⁻¹]
        alpha_s (float): Difusividad térmica del sólido [m²/s]
        
    Parámetros Derivados (Tabla VI):
        A_c (float): Área de flujo del canal [m²]
        D_h (float): Diámetro hidráulico [m]
        P_s (float): Perímetro de intercambio [m]
        l_aire (float): Longitud expuesta por domo [m]
        A_aire (float): Área total expuesta al aire [m²]
        gamma (float): Parámetro de acoplamiento térmico [s⁻¹]
        
    Parámetros de Discretización:
        Nx_fluido (int): Número de nodos en x para fluido
        Nx_placa (int): Número de nodos en x para placa
        Ny_placa (int): Número de nodos en y para placa
        Nr_aleta (int): Número de nodos radiales en aletas
        Ntheta_aleta (int): Número de nodos angulares en aletas
        dx_fluido (float): Espaciamiento en x para fluido [m]
        dx_placa (float): Espaciamiento en x para placa [m]
        dy_placa (float): Espaciamiento en y para placa [m]
        dr_aleta (float): Espaciamiento radial en aletas [m]
        dtheta_aleta (float): Espaciamiento angular en aletas [rad]
        dt (float): Paso de tiempo [s]
        
    Examples:
        >>> params_al = Parametros('Al')
        >>> print(f"Difusividad térmica Al: {params_al.alpha_s:.2e} m²/s")
        >>> params_ss = Parametros('SS')
        >>> print(f"Difusividad térmica SS: {params_ss.alpha_s:.2e} m²/s")
    """
    
    def __init__(self, material: Literal['Al', 'SS'] = 'Al'):
        """
        Inicializa la clase Parametros con el material especificado.
        
        Args:
            material (str): Material del sistema. 'Al' para Aluminio 6061,
                          'SS' para Acero Inoxidable 304. Por defecto 'Al'.
        
        Raises:
            AssertionError: Si el material no es 'Al' o 'SS'.
            AssertionError: Si algún parámetro tiene valores no físicos.
        """
        # Validación del material
        assert material in ['Al', 'SS'], \
            f"Material debe ser 'Al' o 'SS', se recibió '{material}'"
        
        self.material = material
        
        # ========== TABLA I: GEOMETRÍA ==========
        # Referencia: contexto/02_parametros_sistema.md - Tabla I
        
        self.L_x = 0.03  # Longitud en dirección del flujo [m]
        self.W = 0.10    # Ancho/profundidad (eje z) [m]
        self.e_base = 0.01   # Espesor placa base [m]
        self.e_agua = 0.003  # Claro hidráulico canal [m]
        self.D = 0.008       # Diámetro de domos [m]
        self.r = 0.004       # Radio de domos [m] (D/2)
        self.p = 0.010       # Paso entre domos [m]
        self.s = 0.002       # Separación plana [m] (p - D)
        self.N = 3           # Número de domos [adimensional]
        
        # Posiciones de los centros de aletas en eje x [m]
        self.x_aleta_1 = 0.005  # Centro aleta 1 [m]
        self.x_aleta_2 = 0.015  # Centro aleta 2 [m]
        self.x_aleta_3 = 0.025  # Centro aleta 3 [m]
        
        # Validaciones geométricas
        assert self.L_x > 0, "L_x debe ser positivo"
        assert self.W > 0, "W debe ser positivo"
        assert self.e_base > 0, "e_base debe ser positivo"
        assert self.e_agua > 0, "e_agua debe ser positivo"
        assert self.r == self.D / 2, "Radio debe ser D/2"
        assert self.s == self.p - self.D, "Separación debe ser p - D"
        
        # ========== TABLA II: PARÁMETROS DE OPERACIÓN ==========
        # Referencia: contexto/02_parametros_sistema.md - Tabla II
        
        self.Q = 3.33e-5  # Caudal de agua [m³/s] (2 L/min)
        self.u = 0.111    # Velocidad media agua [m/s]
        self.h_agua = 600.0  # Coeficiente convectivo agua [W·m⁻²·K⁻¹]
        self.h_aire = 10.0   # Coeficiente convectivo aire [W·m⁻²·K⁻¹]
        
        # Temperaturas [K]
        self.T_inf = 296.15        # 23°C - Temperatura aire ambiente
        self.T_inicial = 296.15    # 23°C - Temperatura inicial sólido
        self.T_f_in_inicial = 323.15  # 50°C - Temperatura entrada agua inicial
        self.T_f_in = 353.15       # 80°C - Temperatura entrada agua (nueva)
        
        # Validaciones operativas
        assert self.Q > 0, "Caudal debe ser positivo"
        assert self.u > 0, "Velocidad debe ser positiva"
        assert self.h_agua > 0, "h_agua debe ser positivo"
        assert self.h_aire > 0, "h_aire debe ser positivo"
        assert 200 < self.T_inf < 400, "T_inf fuera de rango físico (200-400 K)"
        assert 200 < self.T_inicial < 400, "T_inicial fuera de rango físico"
        assert 200 < self.T_f_in < 400, "T_f_in fuera de rango físico"
        
        # ========== TABLA III: PROPIEDADES DEL AGUA ==========
        # Referencia: contexto/02_parametros_sistema.md - Tabla III
        # Evaluadas a temperatura promedio (~65°C)
        
        self.k_w = 0.563      # Conductividad térmica agua [W·m⁻¹·K⁻¹]
        self.rho_agua = 980.5 # Densidad agua [kg·m⁻³]
        self.cp_agua = 4180.0 # Calor específico agua [J·kg⁻¹·K⁻¹]
        
        # Validaciones propiedades agua
        assert self.k_w > 0, "k_w debe ser positivo"
        assert self.rho_agua > 0, "rho_agua debe ser positivo"
        assert self.cp_agua > 0, "cp_agua debe ser positivo"
        
        # ========== TABLAS IV y V: PROPIEDADES DEL MATERIAL ==========
        # Se inicializan con el material especificado
        self.set_material(material)
        
        # ========== PARÁMETROS DE DISCRETIZACIÓN ==========
        # Referencia: contexto/05_discretizacion_numerica.md
        
        # Malla del fluido (1D)
        self.Nx_fluido = 60
        self.dx_fluido = self.L_x / (self.Nx_fluido - 1)  # ~5.08e-4 m
        
        # Malla de la placa (2D cartesiano)
        self.Nx_placa = 60
        self.Ny_placa = 20
        self.dx_placa = self.L_x / (self.Nx_placa - 1)    # ~5.08e-4 m
        self.dy_placa = self.e_base / (self.Ny_placa - 1) # ~5.26e-4 m
        
        # Malla de las aletas (2D cilíndrico)
        self.Nr_aleta = 10
        self.Ntheta_aleta = 20
        self.dr_aleta = self.r / (self.Nr_aleta - 1)      # ~4.44e-4 m
        self.dtheta_aleta = np.pi / (self.Ntheta_aleta - 1)  # ~0.165 rad
        
        # Paso de tiempo [s]
        # Calcular dinámicamente según material considerando TODOS los criterios:
        # 1. Fourier para placa: Fo_x + Fo_y ≤ 0.5
        # 2. CFL para fluido: u*dt/dx ≤ 1
        # El dt final es el MÍNIMO de ambos
        
        # Criterio Fourier (placa)
        Fo_total_inv = (1.0 / self.dx_placa**2) + (1.0 / self.dy_placa**2)
        dt_max_fourier = 0.5 / (self.alpha_s * Fo_total_inv)
        
        # Criterio CFL (fluido)
        dt_max_cfl = self.dx_fluido / self.u
        
        # Tomar el mínimo (más restrictivo) y usar 80% por seguridad
        dt_max = min(dt_max_fourier, dt_max_cfl)
        self.dt = 0.8 * dt_max
        
        # Validar que dt no sea demasiado pequeño ni grande
        # Rango: 1 μs hasta 50 ms (cubre Al rápido hasta SS lento)
        assert 1e-6 < self.dt < 5e-2, f"dt fuera de rango razonable: {self.dt:.2e} s"
        
        # Validaciones de discretización
        assert self.Nx_fluido > 1, "Nx_fluido debe ser > 1"
        assert self.Nx_placa > 1, "Nx_placa debe ser > 1"
        assert self.Ny_placa > 1, "Ny_placa debe ser > 1"
        assert self.Nr_aleta > 1, "Nr_aleta debe ser > 1"
        assert self.Ntheta_aleta > 1, "Ntheta_aleta debe ser > 1"
        assert self.dt > 0, "dt debe ser positivo"
        
        # Verificar estabilidad (se hace en set_material después de tener alpha_s)
        self._verificar_estabilidad()
    
    def set_material(self, material: Literal['Al', 'SS']) -> None:
        """
        Cambia el material del sistema y actualiza las propiedades termofísicas.
        
        Args:
            material (str): 'Al' para Aluminio 6061, 'SS' para Acero Inoxidable 304
        
        Raises:
            AssertionError: Si el material no es válido
        
        Notes:
            - Aluminio 6061: Alta conductividad (167 W/m·K), respuesta rápida
            - Acero Inox 304: Baja conductividad (16.2 W/m·K), respuesta ~17x más lenta
            
        References:
            - Aluminio: ASM (2019) - Aluminum 6061-T6
            - Acero: Aalco (2005) - Grade 304 Stainless Steel
        """
        assert material in ['Al', 'SS'], \
            f"Material debe ser 'Al' o 'SS', se recibió '{material}'"
        
        self.material = material
        
        if material == 'Al':
            # TABLA IV: ALUMINIO 6061
            # Referencia: contexto/02_parametros_sistema.md - Tabla IV
            self.k_s = 167.0      # Conductividad térmica [W·m⁻¹·K⁻¹]
            self.rho_s = 2700.0   # Densidad [kg·m⁻³]
            self.cp_s = 900.0     # Calor específico [J·kg⁻¹·K⁻¹]
            self.alpha_s = 6.87e-5  # Difusividad térmica [m²/s]
            
        else:  # material == 'SS'
            # TABLA V: ACERO INOXIDABLE 304
            # Referencia: contexto/02_parametros_sistema.md - Tabla V
            self.k_s = 16.2      # Conductividad térmica [W·m⁻¹·K⁻¹]
            self.rho_s = 8000.0  # Densidad [kg·m⁻³]
            self.cp_s = 500.0    # Calor específico [J·kg⁻¹·K⁻¹]
            self.alpha_s = 4.05e-6  # Difusividad térmica [m²/s]
        
        # Verificar cálculo de difusividad térmica: α = k / (ρ·cp)
        alpha_calculado = self.k_s / (self.rho_s * self.cp_s)
        assert np.isclose(self.alpha_s, alpha_calculado, rtol=1e-3), \
            f"Difusividad térmica inconsistente: {self.alpha_s} vs {alpha_calculado}"
        
        # Validaciones de propiedades del sólido
        assert self.k_s > 0, "k_s debe ser positivo"
        assert self.rho_s > 0, "rho_s debe ser positivo"
        assert self.cp_s > 0, "cp_s debe ser positivo"
        assert self.alpha_s > 0, "alpha_s debe ser positivo"
    
    @property
    def A_c(self) -> float:
        """
        Área de flujo del canal de agua [m²].
        
        Returns:
            float: A_c = W × e_agua
            
        Notes:
            Tabla VI: A_c = 3.0×10⁻⁴ m²
        """
        return self.W * self.e_agua
    
    @property
    def D_h(self) -> float:
        """
        Diámetro hidráulico del canal [m].
        
        Returns:
            float: D_h = 2 × e_agua (para canal rectangular muy ancho)
            
        Notes:
            Tabla VI: D_h = 0.006 m
            Aproximación válida porque W >> e_agua
        """
        return 2.0 * self.e_agua
    
    @property
    def P_s(self) -> float:
        """
        Perímetro de intercambio térmico en el canal [m].
        
        Returns:
            float: P_s = W (solo superficie inferior del canal)
            
        Notes:
            Tabla VI: P_s = 0.10 m
            Solo se considera la superficie que contacta con la placa
        """
        return self.W
    
    @property
    def l_aire(self) -> float:
        """
        Longitud expuesta al aire por domo [m].
        
        Returns:
            float: l_aire = π·r + s
            
        Notes:
            Tabla VI: l_aire = 0.01457 m
            Incluye semicircunferencia del domo más separación plana
        """
        return np.pi * self.r + self.s
    
    @property
    def A_aire(self) -> float:
        """
        Área total expuesta al aire [m²].
        
        Returns:
            float: A_aire = l_aire × W × N
            
        Notes:
            Tabla VI: A_aire = 0.004371 m²
            Considera los 3 domos y las superficies planas entre ellos
        """
        return self.l_aire * self.W * self.N
    
    @property
    def gamma(self) -> float:
        """
        Parámetro de acoplamiento térmico fluido-sólido [s⁻¹].
        
        Returns:
            float: γ = h_agua / (ρ_agua · cp_agua · e_agua)
            
        Notes:
            Tabla VI: γ = 4.88×10⁻² s⁻¹
            Caracteriza la intensidad del intercambio térmico.
            Mayor γ → intercambio más rápido.
            
        References:
            Ecuación del fluido: ∂T_f/∂t + u·∂T_f/∂x = -γ(T_f - T_s)
            Ver contexto/03_ecuaciones_gobernantes.md
        """
        return self.h_agua / (self.rho_agua * self.cp_agua * self.e_agua)
    
    @property
    def CFL(self) -> float:
        """
        Número de Courant-Friedrichs-Lewy para el fluido.
        
        Returns:
            float: CFL = u·Δt / Δx
            
        Notes:
            Criterio de estabilidad: CFL ≤ 1
            Valor esperado: ~0.109
            
        References:
            Ver contexto/05_discretizacion_numerica.md - Sección 3
        """
        return self.u * self.dt / self.dx_fluido
    
    @property
    def Fo_x(self) -> float:
        """
        Número de Fourier en dirección x para la placa.
        
        Returns:
            float: Fo_x = α·Δt / Δx²
            
        Notes:
            Para estabilidad en 2D: Fo_x + Fo_y ≤ 0.5
            
        References:
            Ver contexto/05_discretizacion_numerica.md - Sección 3
        """
        return self.alpha_s * self.dt / (self.dx_placa ** 2)
    
    @property
    def Fo_y(self) -> float:
        """
        Número de Fourier en dirección y para la placa.
        
        Returns:
            float: Fo_y = α·Δt / Δy²
            
        Notes:
            Para estabilidad en 2D: Fo_x + Fo_y ≤ 0.5
            
        References:
            Ver contexto/05_discretizacion_numerica.md - Sección 3
        """
        return self.alpha_s * self.dt / (self.dy_placa ** 2)
    
    @property
    def Fo_r(self) -> float:
        """
        Número de Fourier radial para las aletas.
        
        Returns:
            float: Fo_r = α·Δt / Δr²
            
        Notes:
            Para coordenadas cilíndricas: Fo_r + Fo_θ ≤ 0.5
            
        References:
            Ver contexto/05_discretizacion_numerica.md - Sección 3
        """
        return self.alpha_s * self.dt / (self.dr_aleta ** 2)
    
    @property
    def Fo_theta(self) -> float:
        """
        Número de Fourier angular para las aletas (sin normalizar por r²).
        
        Returns:
            float: Fo_θ = α·Δt
            
        Notes:
            En la discretización se divide por r² en cada nodo.
            El término más restrictivo ocurre en r = R (máximo).
            
        References:
            Ver contexto/05_discretizacion_numerica.md - Sección 4.4
        """
        return self.alpha_s * self.dt
    
    def _verificar_estabilidad(self) -> None:
        """
        Verifica que los criterios de estabilidad numérica se cumplan.
        
        Raises:
            AssertionError: Si CFL > 1 o Fourier > 0.5
            
        Notes:
            - CFL ≤ 1: Estabilidad del esquema upwind en fluido
            - Fourier ≤ 0.5: Estabilidad del esquema FTCS en sólidos
        """
        # Criterio CFL para fluido
        cfl = self.CFL
        assert cfl <= 1.0, \
            f"Inestabilidad: CFL = {cfl:.3f} > 1.0. Reducir dt o aumentar dx_fluido"
        
        # Criterio de Fourier para placa (2D)
        fourier_placa = self.Fo_x + self.Fo_y
        assert fourier_placa <= 0.5, \
            f"Inestabilidad en placa: Fo_x + Fo_y = {fourier_placa:.3f} > 0.5. " \
            f"Reducir dt o aumentar dx/dy"
        
        # Criterio de Fourier para aletas (2D cilíndrico)
        # El término más restrictivo es en r = R
        fourier_aleta = self.Fo_r + self.Fo_theta / (self.r ** 2)
        assert fourier_aleta <= 0.5, \
            f"Inestabilidad en aletas: Fo_r + Fo_θ/r² = {fourier_aleta:.3f} > 0.5. " \
            f"Reducir dt o aumentar dr/dθ"
    
    def __str__(self) -> str:
        """
        Representación en string de los parámetros principales.
        
        Returns:
            str: Resumen de parámetros clave
        """
        return f"""
Parámetros del Sistema de Enfriamiento GPU
==========================================
Material: {self.material}

Geometría:
  L_x = {self.L_x} m
  W = {self.W} m
  e_base = {self.e_base} m
  e_agua = {self.e_agua} m
  N_domos = {self.N}

Propiedades del material:
  k_s = {self.k_s} W/(m·K)
  ρ_s = {self.rho_s} kg/m³
  cp_s = {self.cp_s} J/(kg·K)
  α_s = {self.alpha_s:.2e} m²/s

Discretización:
  Nx_placa = {self.Nx_placa}
  Ny_placa = {self.Ny_placa}
  dt = {self.dt:.2e} s

Estabilidad:
  CFL = {self.CFL:.3f} (debe ser ≤ 1.0)
  Fo_placa = {self.Fo_x + self.Fo_y:.3f} (debe ser ≤ 0.5)

Temperaturas:
  T_aire = {self.T_inf - 273.15:.1f} °C
  T_agua_in = {self.T_f_in - 273.15:.1f} °C
"""
    
    def __repr__(self) -> str:
        """
        Representación técnica de la clase.
        
        Returns:
            str: String con información de la instancia
        """
        return f"Parametros(material='{self.material}')"


# Ejemplo de uso
if __name__ == "__main__":
    # Crear parámetros para Aluminio
    print("=" * 60)
    print("ALUMINIO 6061")
    print("=" * 60)
    params_al = Parametros('Al')
    print(params_al)
    
    # Crear parámetros para Acero Inoxidable
    print("\n" + "=" * 60)
    print("ACERO INOXIDABLE 304")
    print("=" * 60)
    params_ss = Parametros('SS')
    print(params_ss)
    
    # Comparación de difusividades
    ratio = params_al.alpha_s / params_ss.alpha_s
    print("\n" + "=" * 60)
    print("COMPARACIÓN")
    print("=" * 60)
    print(f"α_Al / α_SS = {ratio:.1f}")
    print(f"El aluminio responde ~{ratio:.0f} veces más rápido que el acero")

