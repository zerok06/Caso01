#!/bin/bash

# Script para configurar credenciales de GCP para desarrollo local

echo "=================================================="
echo "Configuración de GCP para Desarrollo Local"
echo "=================================================="
echo ""

# Detectar ruta del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$SCRIPT_DIR/.env"
KEY_FILE="$SCRIPT_DIR/caso01-gcp-key.json"

echo "📁 Directorios detectados:"
echo "   • Proyecto: $PROJECT_ROOT"
echo "   • Backend: $SCRIPT_DIR"
echo "   • Archivo .env: $ENV_FILE"
echo "   • Credenciales: $KEY_FILE"
echo ""

# Verificar que existe el archivo de credenciales
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ ERROR: No se encuentra el archivo de credenciales"
    echo "   Buscando: $KEY_FILE"
    echo ""
    echo "   Posibles soluciones:"
    echo "   1. Asegúrate de que el archivo caso01-gcp-key.json existe"
    echo "   2. Descárgalo desde la consola de GCP"
    echo "   3. Colócalo en: $SCRIPT_DIR/"
    echo ""
    exit 1
fi

echo "✅ Archivo de credenciales encontrado"
echo ""

# Verificar que existe .env
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ ERROR: No se encuentra el archivo .env"
    echo "   Buscando: $ENV_FILE"
    echo ""
    exit 1
fi

echo "✅ Archivo .env encontrado"
echo ""

# Crear backup del .env
BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo "💾 Backup creado: $(basename $BACKUP_FILE)"
echo ""

# Actualizar GOOGLE_APPLICATION_CREDENTIALS
echo "🔧 Actualizando GOOGLE_APPLICATION_CREDENTIALS..."

# Buscar y reemplazar la línea
if grep -q "^GOOGLE_APPLICATION_CREDENTIALS=" "$ENV_FILE"; then
    # Reemplazar línea existente
    sed -i "s|^GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE|" "$ENV_FILE"
    echo "   ✅ Línea actualizada"
else
    # Agregar línea si no existe
    echo "GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE" >> "$ENV_FILE"
    echo "   ✅ Línea agregada"
fi

echo ""
echo "=================================================="
echo "✅ Configuración completada"
echo "=================================================="
echo ""
echo "Siguiente paso: Validar el bucket"
echo ""
echo "  cd $PROJECT_ROOT"
echo "  .venv/bin/python backend/validate_gcs_bucket.py"
echo ""
echo "Si el bucket no existe o no tienes permisos, revisa:"
echo "  SOLUCION_BUCKET_GCS.md"
echo ""
