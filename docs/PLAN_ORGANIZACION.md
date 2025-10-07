# 📂 Plan de Organización del Repositorio

## 🎯 Objetivo
Organizar el repositorio para entrega profesional, separando:
- Código fuente
- Scripts auxiliares
- Documentación
- Logs
- Resultados

---

## 📁 Estructura Propuesta

```
python-adrian/
│
├── src/                          # ✅ Código fuente principal (NO MOVER)
│   ├── parametros.py
│   ├── mallas.py
│   ├── fluido.py
│   ├── placa.py
│   ├── aletas.py
│   ├── acoplamiento.py
│   ├── solucionador.py
│   └── visualizacion.py
│
├── tests/                        # ✅ Pruebas (NO MOVER)
│
├── contexto/                     # ✅ Documentación del problema (NO MOVER)
│   ├── 00_guia_implementacion.md
│   ├── 01_contexto_proyecto.md
│   ├── 02_parametros_sistema.md
│   ├── 03_ecuaciones_gobernantes.md
│   ├── 04_condiciones_frontera.md
│   ├── 05_discretizacion_numerica.md
│   └── 06_herramientas_desarrollo.md
│
├── resultados/                   # ✅ Datos y figuras (NO MOVER)
│   ├── datos/
│   └── figuras/
│
├── docs/                         # 📝 Documentación adicional
│   ├── adr/                      # ✅ Ya existe
│   ├── analisis/                 # 🆕 Análisis e informes
│   │   ├── ANALISIS_INGENIERIL_RESULTADOS.md
│   │   ├── ENTREGABLES_PRESENTACION.md
│   │   └── codigo_resumen_presentacion.py
│   ├── guias/                    # 🆕 Guías de uso
│   │   ├── INSTRUCCIONES_USO.txt
│   │   ├── COMANDOS_STREAMLIT.txt
│   │   └── README_INTERFAZ.md
│   └── notas/                    # 🆕 Notas de desarrollo
│       ├── ACTUALIZACION_PROGRESO.md
│       ├── CORRECCION_ATRIBUTOS.md
│       ├── DISTRIBUCION_ESPACIAL.md
│       ├── RESUMEN_CONVERGENCIA.md
│       ├── TEST_MAIN.md
│       └── INSTRUCCIONES_VISUALIZACIONES_SS.md
│
├── scripts/                      # 🆕 Scripts auxiliares
│   ├── simulacion/               # Scripts de simulación
│   │   ├── simular_acero.py
│   │   └── generar_grafico_convergencia.py
│   ├── visualizacion/            # Scripts de visualización
│   │   ├── generar_grafico_rapido.py
│   │   ├── generar_visualizaciones_SS.py
│   │   └── ejemplo_distribucion_espacial.py
│   └── utilidades/               # Scripts de monitoreo
│       ├── monitorear_convergencia.sh
│       └── monitorear_simulacion_SS.sh
│
├── logs/                         # 🆕 Logs de ejecución
│   ├── convergencia_output.log
│   ├── simulacion_SS.log
│   ├── simulacion_log.txt
│   ├── streamlit.log
│   └── visualizacion_output.log
│
├── todo/                         # ✅ Tareas pendientes (NO MOVER)
│   └── instrucciones_ecuaciones.md
│
├── main.py                       # ✅ Punto de entrada CLI (MANTENER EN ROOT)
├── interfaz_web.py               # ✅ Punto de entrada Web (MANTENER EN ROOT)
├── requirements.txt              # ✅ Dependencias (MANTENER EN ROOT)
├── README.md                     # ✅ README principal (MANTENER EN ROOT)
├── worklog.md                    # ✅ Registro de trabajo (MANTENER EN ROOT)
├── .gitignore                    # ✅ Git ignore (MANTENER EN ROOT)
└── .streamlit/                   # ✅ Config Streamlit (MANTENER EN ROOT)
```

---

## 🔄 Acciones a Realizar

### 1. Crear nuevas carpetas:
- `docs/analisis/`
- `docs/guias/`
- `docs/notas/`
- `scripts/simulacion/`
- `scripts/visualizacion/`
- `scripts/utilidades/`
- `logs/`

### 2. Mover archivos:

#### A `docs/analisis/`:
- ✅ ANALISIS_INGENIERIL_RESULTADOS.md
- ✅ ENTREGABLES_PRESENTACION.md
- ✅ codigo_resumen_presentacion.py

#### A `docs/guias/`:
- ✅ INSTRUCCIONES_USO.txt
- ✅ COMANDOS_STREAMLIT.txt
- ✅ README_INTERFAZ.md

#### A `docs/notas/`:
- ✅ ACTUALIZACION_PROGRESO.md
- ✅ CORRECCION_ATRIBUTOS.md
- ✅ DISTRIBUCION_ESPACIAL.md
- ✅ RESUMEN_CONVERGENCIA.md
- ✅ TEST_MAIN.md
- ✅ INSTRUCCIONES_VISUALIZACIONES_SS.md

#### A `scripts/simulacion/`:
- ✅ simular_acero.py
- ✅ generar_grafico_convergencia.py

#### A `scripts/visualizacion/`:
- ✅ generar_grafico_rapido.py
- ✅ generar_visualizaciones_SS.py
- ✅ ejemplo_distribucion_espacial.py

#### A `scripts/utilidades/`:
- ✅ monitorear_convergencia.sh
- ✅ monitorear_simulacion_SS.sh

#### A `logs/`:
- ✅ convergencia_output.log
- ✅ simulacion_SS.log
- ✅ simulacion_log.txt
- ✅ streamlit.log
- ✅ visualizacion_output.log

### 3. Actualizar imports:
- ❓ Verificar scripts que usan `sys.path` o imports relativos
- ❓ Ajustar rutas si es necesario

### 4. Actualizar README.md:
- 📝 Explicar nueva estructura
- 📝 Cómo ejecutar desde nuevas ubicaciones
- 📝 Guía de navegación

---

## ⚠️ Archivos que NO se moverán
- `main.py` → Punto de entrada principal
- `interfaz_web.py` → Punto de entrada web
- `requirements.txt` → Debe estar en root
- `worklog.md` → Historial de trabajo
- `.gitignore` → Configuración git
- Carpetas `src/`, `tests/`, `contexto/`, `resultados/`, `todo/` → Ya organizadas

---

## ✅ Beneficios
1. **Claridad**: Separación clara de responsabilidades
2. **Navegación**: Más fácil encontrar archivos
3. **Profesional**: Estructura estándar de proyectos Python
4. **Mantenimiento**: Más fácil agregar nuevos scripts/docs
5. **Limpieza**: Root folder solo con puntos de entrada y configs

---

**¿Procedo con la reorganización?**
