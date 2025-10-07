#!/bin/bash
# Monitor de progreso simulación SS

echo "=========================================="
echo "MONITOR: Simulación Acero Inoxidable"
echo "=========================================="
echo ""

# Verificar si está corriendo
if pgrep -f "simular_acero.py" > /dev/null; then
    echo "✅ Simulación en ejecución..."
    echo ""
    
    if [ -f simulacion_SS.log ]; then
        echo "📊 Últimas 20 líneas:"
        echo "------------------------------------------"
        tail -n 20 simulacion_SS.log
        echo "------------------------------------------"
    else
        echo "⚠️  Log aún no creado..."
    fi
else
    echo "⏹️  Simulación no está corriendo"
    echo ""
    
    if [ -f simulacion_SS.log ]; then
        echo "📊 Resultado final:"
        echo "------------------------------------------"
        tail -n 30 simulacion_SS.log
        echo "------------------------------------------"
        
        # Verificar archivo de resultados
        if [ -f resultados/datos/resultados_Stainless_Steel.npz ]; then
            echo ""
            echo "✅ Archivo de resultados generado:"
            ls -lh resultados/datos/resultados_Stainless_Steel.npz
        fi
    fi
fi

echo ""
echo "=========================================="
