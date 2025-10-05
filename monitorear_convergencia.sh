#!/bin/bash
# Script para monitorear el progreso de la simulación hacia convergencia

echo "=========================================="
echo "MONITOR DE CONVERGENCIA"
echo "=========================================="
echo ""

# Verificar si el proceso está corriendo
if pgrep -f "generar_grafico_convergencia.py" > /dev/null; then
    echo "✅ Simulación en ejecución..."
    echo ""
    
    # Mostrar últimas 20 líneas del log
    if [ -f convergencia_output.log ]; then
        echo "📊 Últimas actualizaciones:"
        echo "------------------------------------------"
        tail -n 20 convergencia_output.log
        echo "------------------------------------------"
        echo ""
        
        # Extraer tiempo actual y max|dT/dt|
        ultima_linea=$(tail -n 1 convergencia_output.log)
        if [[ $ultima_linea == *"t="* ]]; then
            echo "⏱️  Estado actual extraído del log"
        fi
    else
        echo "⚠️  Log aún no creado, iniciando..."
    fi
    
    echo ""
    echo "💡 Comandos útiles:"
    echo "   - Ver progreso en tiempo real: tail -f convergencia_output.log"
    echo "   - Ver últimas líneas: tail -n 50 convergencia_output.log"
    echo "   - Detener simulación: pkill -f generar_grafico_convergencia.py"
    
else
    echo "⏹️  Simulación no está corriendo"
    echo ""
    
    if [ -f convergencia_output.log ]; then
        echo "📊 Resultado final:"
        echo "------------------------------------------"
        tail -n 30 convergencia_output.log
        echo "------------------------------------------"
        
        # Verificar si se generaron las figuras
        echo ""
        echo "📁 Verificando figuras generadas:"
        ls -lh resultados/figuras/distribucion_espacial_convergencia*.png 2>/dev/null || echo "   ⚠️  Figuras aún no generadas"
        ls -lh resultados/figuras/distribucion_espacial_final*.png 2>/dev/null || echo "   ⚠️  Figura final aún no generada"
    else
        echo "⚠️  No se encontró log de ejecución"
    fi
fi

echo ""
echo "=========================================="
