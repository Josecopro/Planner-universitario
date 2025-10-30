#!/bin/bash

# Script para verificar la configuración de Supabase
# Autor: Sistema de Desarrollo
# Fecha: Octubre 2025

echo "🔍 Verificando configuración de Supabase..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio frontend/"
    exit 1
fi

# Verificar archivo .env
echo "📄 Verificando archivo .env..."
if [ -f ".env" ]; then
    echo "✅ Archivo .env encontrado"
    
    # Verificar variables
    if grep -q "VITE_SUPABASE_URL" .env; then
        echo "✅ VITE_SUPABASE_URL configurada"
    else
        echo "❌ VITE_SUPABASE_URL no encontrada"
    fi
    
    if grep -q "VITE_SUPABASE_ANON_KEY" .env; then
        echo "✅ VITE_SUPABASE_ANON_KEY configurada"
    else
        echo "❌ VITE_SUPABASE_ANON_KEY no encontrada"
    fi
else
    echo "❌ Archivo .env no encontrado"
    echo "💡 Crea un archivo .env con:"
    echo "   VITE_SUPABASE_URL=tu_url"
    echo "   VITE_SUPABASE_ANON_KEY=tu_key"
    exit 1
fi

echo ""
echo "📦 Verificando dependencias..."

# Verificar que node_modules existe
if [ -d "node_modules" ]; then
    echo "✅ node_modules encontrado"
else
    echo "⚠️  node_modules no encontrado"
    echo "💡 Ejecuta: npm install"
    exit 1
fi

# Verificar que @supabase/supabase-js está instalado
if [ -d "node_modules/@supabase/supabase-js" ]; then
    echo "✅ @supabase/supabase-js instalado"
else
    echo "❌ @supabase/supabase-js no instalado"
    echo "💡 Ejecuta: npm install @supabase/supabase-js"
    exit 1
fi

echo ""
echo "📁 Verificando archivos de configuración..."

# Verificar archivos creados
if [ -f "src/config/supabase.js" ]; then
    echo "✅ src/config/supabase.js encontrado"
else
    echo "⚠️  src/config/supabase.js no encontrado"
fi

if [ -f "src/services/supabase.service.js" ]; then
    echo "✅ src/services/supabase.service.js encontrado"
else
    echo "⚠️  src/services/supabase.service.js no encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Configuración verificada exitosamente"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Para usar Supabase, ejecuta:"
echo "   npm run dev"
echo ""
echo "⚠️  IMPORTANTE: NO uses 'node archivo.js' directamente"
echo "   Usa siempre el servidor de desarrollo de Vite"
echo ""