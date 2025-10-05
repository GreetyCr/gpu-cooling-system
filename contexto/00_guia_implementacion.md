# Guía Rápida de Implementación

## Resumen Ejecutivo del Proyecto

**Objetivo:** Simular el comportamiento transitorio de un sistema de enfriamiento líquido para GPU cuando la temperatura del agua cambia de 50°C a 80°C.

**Materiales a comparar:** Aluminio 6061 vs Acero Inoxidable 304

**Método:** Solución numérica de ecuaciones de conducción-convección de calor usando diferencias finitas explícitas.

---

## Flujo de Trabajo Recomendado

### Fase 1: Configuración (30-60 min)
1. Leer todos los archivos .md en orden (01 a 06)
2. Configurar entorno Python con las librerías necesarias
3. Crear estructura de carpetas del proyecto

### Fase 2: Implementación Core (4-6 horas)
1. **parametros.py**: Definir todas las constantes y parámetros
2. **mallas.py**: Generar mallas para fluido, placa y aletas
3. **fluido.py**: Implementar solver 1D con upwind
4. **placa.py**: Implementar solver 2D cartesiano (FTCS)
5. **aletas.py**: Implementar solver 2D cilíndrico (FTCS)

### Fase 3: Acoplamiento (2-3 horas)
1. **acoplamiento.py**: Implementar interfaz placa-aleta
2. **solucionador.py**: Integrar todos los dominios en bucle temporal
3. Verificar conservación de energía

### Fase 4: Validación y Visualización (2-3 horas)
1. **tests/**: Escribir tests unitarios
2. **visualizacion.py**: Crear funciones de graficación
3. Ejecutar casos de prueba
4. Comparar Aluminio vs Acero Inoxidable

### Fase 5: Análisis (2-4 horas)
1. Ejecutar simulaciones completas
2. Generar gráficos y animaciones
3. Determinar criterio de estado estacionario
4. Documentar resultados

---

## Orden de Lectura de Archivos .md

| # | Archivo | Propósito | Tiempo |
|---|---------|-----------|--------|
| 0 | **00_GUIA_RAPIDA_IMPLEMENTACION.md** | Orientación general | 5 min |
| 1 | **01_contexto_proyecto.md** | Entender el problema | 10 min |
| 2 | **02_parametros_sistema.md** | Conocer todos los valores | 15 min |
| 3 | **03_ecuaciones_gobernantes.md** | Ecuaciones diferenciales | 20 min |
| 4 | **04_condiciones_frontera.md** | Condiciones de borde | 20 min |
| 5 | **05_discretizacion_numerica.md** | Esquemas numéricos | 30 min |
| 6 | **06_herramientas_desarrollo.md** | Setup de herramientas | 15 min |

**Total tiempo de lectura:** ~2 horas

---

## Información Crítica para el Agente de IA

### Restricciones Fundamentales

1. **Estabilidad Numérica:**
   - Paso de tiempo: $\Delta t = 5 \times 10^{-4}$ s (0.5 ms)
   - CFL < 1 para fluido
   - Fourier < 0.5 para sólidos

2. **Dominios:**
   - Fluido: 1D, 60 nodos
   - Placa: 2D cartesiano, 60×20 nodos
   - Aletas: 2D cilíndrico, 10×20 nodos × 3 aletas
   - **Total: 1,860 nodos**

3. **Propiedades Clave:**
   - $\alpha_{Al} = 6.87 \times 10^{-5}$ m²/s
   - $\alpha_{SS} = 4.05 \times 10^{-6}$ m²/s
   - Relación: $\alpha_{Al} / \alpha_{SS} \approx 17$

4. **Acoplamientos:**
   - Fluido ↔ Placa: Convección en y=0
   - Placa ↔ Aleta: Continuidad en diámetro
   - Sólido ↔ Aire: Convección en superficies superiores

---

## Ecuaciones Esenciales (Quick Reference)

### Fluido (1D)
$$\frac{\partial T_f}{\partial t} + u \frac{\partial T_f}{\partial x} = -\gamma (T_f - T_s)$$

**Discretización:**
$$T_{f,i}^{n+1} = T_{f,i}^n - CFL(T_{f,i}^n - T_{f,i-1}^n) - \gamma \Delta t (T_{f,i}^n - T_{s,i}^n)$$

### Placa (2D)
$$\frac{\partial T}{\partial t} = \alpha \left( \frac{\partial^2 T}{\partial x^2} + \frac{\partial^2 T}{\partial y^2} \right)$$

**Discretización:**
$$T_{i,j}^{n+1} = T_{i,j}^n + Fo_x(T_{i+1,j}^n - 2T_{i,j}^n + T_{i-1,j}^n) + Fo_y(T_{i,j+1}^n - 2T_{i,j}^n + T_{i,j-1}^n)$$

### Aletas (2D cilíndrico)
$$\frac{\partial T}{\partial t} = \alpha \left( \frac{\partial^2 T}{\partial r^2} + \frac{1}{r} \frac{\partial T}{\partial r} + \frac{1}{r^2} \frac{\partial^2 T}{\partial \theta^2} \right)$$

---

## Checklist de Implementación

### Módulo: parametros.py
- [ ] Definir constantes geométricas (L_x, W, e_base, etc.)
- [ ] Definir propiedades de materiales (k, ρ, c_p, α)
- [ ] Definir parámetros operativos (u, h_agua, h_aire)
- [ ] Calcular parámetros derivados (A_c, γ, D_h)
- [ ] Función para cambiar entre Al y SS

### Módulo: mallas.py
- [ ] Generar malla 1D para fluido (60 nodos)
- [ ] Generar malla 2D para placa (60×20 nodos)
- [ ] Generar malla 2D cilíndrica para aletas (10×20 nodos, ×3)
- [ ] Función para visualizar mallas

### Módulo: fluido.py
- [ ] Inicializar campo de temperatura
- [ ] Implementar esquema upwind
- [ ] Condición de frontera entrada (Dirichlet)
- [ ] Condición de frontera salida (Neumann)
- [ ] Función de actualización temporal
- [ ] Función para extraer T_s desde placa

### Módulo: placa.py
- [ ] Inicializar campo de temperatura
- [ ] Implementar FTCS 2D
- [ ] BC de convección agua (y=0) con nodos fantasma
- [ ] BC de convección aire (y=e_base) con nodos fantasma
- [ ] BC laterales (x=0, x=L_x)
- [ ] Función de actualización temporal

### Módulo: aletas.py
- [ ] Inicializar campo de temperatura (×3 aletas)
- [ ] Implementar FTCS cilíndrico
- [ ] Tratamiento de singularidad en r=0 (L'Hôpital)
- [ ] BC de convección aire (r=R)
- [ ] BC de interfaz (θ=0, θ=π)
- [ ] Función de actualización temporal para cada aleta

### Módulo: acoplamiento.py
- [ ] Función de interpolación bilineal cartesiana-polar
- [ ] Función para extraer T de placa en interfaz
- [ ] Función para imponer T en aleta desde placa
- [ ] Verificar continuidad de flujo de calor
- [ ] Función de acoplamiento fluido-placa

### Módulo: solucionador.py
- [ ] Bucle temporal principal
- [ ] Secuencia de actualización (fluido → placa → aletas)
- [ ] Criterio de convergencia a estado estacionario
- [ ] Almacenamiento de resultados
- [ ] Balance energético global
- [ ] Barra de progreso

### Módulo: visualizacion.py
- [ ] Gráfico de perfil de temperatura 1D (fluido)
- [ ] Contornos 2D de temperatura (placa)
- [ ] Contornos polares de temperatura (aletas)
- [ ] Gráfico de evolución temporal en puntos clave
- [ ] Animación del transitorio
- [ ] Comparación Al vs SS

---

## Estructura Mínima de Código

### main.py - Esqueleto
```python
import numpy as np
from src.parametros import Parametros
from src.mallas import generar_mallas
from src.solucionador import Solucionador
from src.visualizacion import graficar_resultados

def main():
    # Configuración
    material = 'Al'  # o 'SS'
    params = Parametros(material)
    
    # Generar mallas
    mallas = generar_mallas(params)
    
    # Inicializar solucionador
    solver = Solucionador(params, mallas)
    
    # Ejecutar simulación
    resultados = solver.resolver(t_final=10.0)
    
    # Visualizar
    graficar_resultados(resultados, material)
    
if __name__ == '__main__':
    main()
```

---

## Métricas de Evaluación

### Criterio de Estado Estacionario
Definir que el sistema alcanzó equilibrio cuando:

$$\max_{i,j} \left| \frac{T_{i,j}^{n+1} - T_{i,j}^n}{\Delta t} \right| < \epsilon$$

Donde $\epsilon = 10^{-3}$ K/s (o ajustar según necesidad)

### Balance Energético
Verificar en cada paso:

$$\left| \dot{Q}_{in} - \dot{Q}_{out} - \frac{dE}{dt} \right| < \text{tolerancia}$$

Donde:
- $\dot{Q}_{in} = \dot{m} c_{p,agua} (T_{f,in} - T_{f,out})$
- $\dot{Q}_{out} = h_{aire} A_{aire} (T_{superficie} - T_\infty)$
- $E = \sum \rho c_p V T$

---

## Resultados Esperados

### Comparación Al vs SS

| Material | $\alpha$ (m²/s) | Tiempo a 95% equilibrio (est.) |
|----------|-----------------|-------------------------------|
| Aluminio | $6.87 \times 10^{-5}$ | ~0.5 - 2 s |
| Acero Inox. | $4.05 \times 10^{-6}$ | ~8 - 30 s |

### Gráficos a Generar

1. **Evolución temporal de T en punto central de placa**
2. **Perfiles de temperatura a lo largo de x en diferentes tiempos**
3. **Contornos 2D de la placa en t_final**
4. **Distribución de T en aletas (gráfico polar)**
5. **Comparación directa Al vs SS**
6. **Animación del proceso transitorio**

---

## Troubleshooting Común

### Problema: Inestabilidad numérica (valores NaN o infinito)
**Solución:** Reducir $\Delta t$, verificar CFL y Fourier

### Problema: El sistema no converge
**Solución:** Verificar condiciones de frontera, revisar acoplamiento fluido-sólido

### Problema: Discontinuidad en interfaz placa-aleta
**Solución:** Mejorar interpolación, verificar continuidad de flujo

### Problema: Balance energético no se conserva
**Solución:** Revisar implementación de BCs, verificar cálculo de áreas

### Problema: Simulación muy lenta
**Solución:** Usar `numba`, reducir densidad de malla, paralelizar aletas

---

## Contacto y Soporte

Este proyecto es parte del curso **IQ-0331 Fenómenos de Transferencia**  
Universidad de Costa Rica  
Profesor: PH.D Leonardo Garro Mena  
Estudiante: Adrián Vargas Tijerino (C18332)

---

## Próximos Pasos Después de Implementación

1. Validar con casos simples (placa infinita, cilindro, etc.)
2. Análisis de sensibilidad a parámetros (h, Δt, Δx)
3. Comparación con solución analítica simplificada
4. Optimización de performance
5. Extensión a 3D (opcional)
6. Acoplamiento con modelo de GPU (opcional)

---

**¡Buena suerte con la implementación!**
