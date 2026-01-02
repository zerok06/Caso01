"""
Script para validar que el bucket de Google Cloud Storage existe y está configurado correctamente.
"""

import os
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Cambiar al directorio backend para que settings cargue el .env correcto
os.chdir(backend_dir)

from google.cloud import storage
from google.api_core import exceptions
from core.config import settings

def validate_gcs_bucket():
    """
    Valida la configuración y existencia del bucket de GCS.
    """
    print("=" * 80)
    print("VALIDACIÓN DE GOOGLE CLOUD STORAGE BUCKET")
    print("=" * 80)
    print()
    
    # 1. Verificar variables de entorno
    print("📋 PASO 1: Verificando configuración...")
    print("-" * 80)
    
    project_id = settings.GOOGLE_CLOUD_PROJECT
    bucket_name = settings.GCS_BUCKET_NAME
    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    print(f"   • Project ID: {project_id or '❌ NO CONFIGURADO'}")
    print(f"   • Bucket Name: {bucket_name or '❌ NO CONFIGURADO'}")
    print(f"   • Credentials Path: {credentials_path or '❌ NO CONFIGURADO'}")
    print()
    
    if not project_id:
        print("❌ ERROR: GOOGLE_CLOUD_PROJECT no está configurado en .env")
        print("   Agrega: GOOGLE_CLOUD_PROJECT=tu-proyecto-id")
        return False
        
    if not bucket_name:
        print("❌ ERROR: GCS_BUCKET_NAME no está configurado en .env")
        print("   Agrega: GCS_BUCKET_NAME=tu-bucket-name")
        return False
    
    # 2. Verificar archivo de credenciales
    print("🔑 PASO 2: Verificando credenciales...")
    print("-" * 80)
    
    if credentials_path:
        cred_file = Path(credentials_path)
        if cred_file.exists():
            print(f"   ✅ Archivo de credenciales encontrado: {credentials_path}")
        else:
            print(f"   ❌ ERROR: Archivo de credenciales no encontrado: {credentials_path}")
            return False
    else:
        print("   ⚠️  ADVERTENCIA: GOOGLE_APPLICATION_CREDENTIALS no configurado")
        print("   Se intentará usar Application Default Credentials")
    print()
    
    # 3. Intentar conectar con GCS
    print("🌐 PASO 3: Conectando con Google Cloud Storage...")
    print("-" * 80)
    
    try:
        client = storage.Client(project=project_id)
        print(f"   ✅ Cliente de Storage inicializado correctamente")
        print(f"   • Proyecto: {client.project}")
    except Exception as e:
        print(f"   ❌ ERROR al inicializar cliente de Storage:")
        print(f"   {str(e)}")
        print()
        print("   Posibles soluciones:")
        print("   1. Verifica que el archivo JSON de credenciales sea válido")
        print("   2. Asegúrate de tener permisos de Storage en el proyecto")
        print("   3. Ejecuta: gcloud auth application-default login")
        return False
    print()
    
    # 4. Verificar que el bucket existe
    print("🪣 PASO 4: Verificando existencia del bucket...")
    print("-" * 80)
    
    try:
        bucket = client.bucket(bucket_name)
        
        # Intentar acceder al bucket (esto lanza excepción si no existe)
        if bucket.exists():
            print(f"   ✅ Bucket '{bucket_name}' existe y es accesible")
            
            # Obtener información del bucket
            bucket.reload()
            print(f"   • Location: {bucket.location}")
            print(f"   • Storage Class: {bucket.storage_class}")
            print(f"   • Created: {bucket.time_created}")
            
        else:
            print(f"   ❌ ERROR: El bucket '{bucket_name}' NO EXISTE")
            print()
            print("   Para crear el bucket, ejecuta:")
            print(f"   gsutil mb -p {project_id} -c STANDARD -l US gs://{bucket_name}")
            print()
            print("   O créalo desde la consola de GCP:")
            print(f"   https://console.cloud.google.com/storage/browser?project={project_id}")
            return False
            
    except exceptions.Forbidden as e:
        print(f"   ❌ ERROR: Sin permisos para acceder al bucket '{bucket_name}'")
        print(f"   {str(e)}")
        print()
        print("   Posibles soluciones:")
        print("   1. Verifica que la cuenta de servicio tenga rol 'Storage Object Admin'")
        print("   2. Verifica que el proyecto sea correcto")
        return False
        
    except exceptions.NotFound:
        print(f"   ❌ ERROR: El bucket '{bucket_name}' NO EXISTE en el proyecto '{project_id}'")
        print()
        print("   Para crear el bucket, ejecuta:")
        print(f"   gsutil mb -p {project_id} -c STANDARD -l US gs://{bucket_name}")
        print()
        print("   O créalo desde la consola de GCP:")
        print(f"   https://console.cloud.google.com/storage/browser?project={project_id}")
        return False
        
    except Exception as e:
        print(f"   ❌ ERROR al verificar bucket:")
        print(f"   {str(e)}")
        return False
    print()
    
    # 5. Probar operaciones de escritura/lectura
    print("🧪 PASO 5: Probando operaciones en el bucket...")
    print("-" * 80)
    
    test_blob_name = "_test_validation.txt"
    test_content = b"Test content from validation script"
    
    try:
        # Intentar escribir
        print(f"   • Escribiendo archivo de prueba: {test_blob_name}")
        blob = bucket.blob(test_blob_name)
        blob.upload_from_string(test_content)
        print(f"   ✅ Escritura exitosa")
        
        # Intentar leer
        print(f"   • Leyendo archivo de prueba...")
        downloaded_content = blob.download_as_bytes()
        
        if downloaded_content == test_content:
            print(f"   ✅ Lectura exitosa - contenido verificado")
        else:
            print(f"   ⚠️  ADVERTENCIA: El contenido leído no coincide")
        
        # Limpiar archivo de prueba
        print(f"   • Eliminando archivo de prueba...")
        blob.delete()
        print(f"   ✅ Eliminación exitosa")
        
    except exceptions.Forbidden:
        print(f"   ❌ ERROR: Sin permisos para escribir/leer en el bucket")
        print()
        print("   La cuenta de servicio necesita el rol 'Storage Object Admin'")
        return False
        
    except Exception as e:
        print(f"   ❌ ERROR en operaciones de prueba:")
        print(f"   {str(e)}")
        return False
    print()
    
    # 6. Listar algunos objetos (si existen)
    print("📁 PASO 6: Listando archivos en el bucket...")
    print("-" * 80)
    
    try:
        blobs = list(client.list_blobs(bucket_name, max_results=10))
        
        if blobs:
            print(f"   ℹ️  Bucket contiene archivos (mostrando primeros 10):")
            for blob in blobs:
                size_mb = blob.size / (1024 * 1024)
                print(f"      • {blob.name} ({size_mb:.2f} MB)")
        else:
            print(f"   ℹ️  Bucket está vacío (sin archivos)")
            
    except Exception as e:
        print(f"   ⚠️  No se pudo listar archivos: {str(e)}")
    print()
    
    # Resumen final
    print("=" * 80)
    print("✅ VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print()
    print(f"El bucket '{bucket_name}' está correctamente configurado y operativo.")
    print()
    print("Siguiente paso:")
    print("  • Ya puedes subir documentos desde la aplicación")
    print("  • Los archivos se guardarán en: gs://{}/".format(bucket_name))
    print()
    
    return True


def show_create_bucket_instructions():
    """
    Muestra instrucciones detalladas para crear el bucket.
    """
    print()
    print("=" * 80)
    print("📖 INSTRUCCIONES PARA CREAR EL BUCKET")
    print("=" * 80)
    print()
    
    bucket_name = settings.GCS_BUCKET_NAME
    project_id = settings.GOOGLE_CLOUD_PROJECT
    
    print("OPCIÓN 1: Usando gcloud CLI")
    print("-" * 80)
    print()
    print("1. Asegúrate de tener gcloud instalado y autenticado:")
    print("   gcloud auth login")
    print()
    print("2. Selecciona tu proyecto:")
    print(f"   gcloud config set project {project_id}")
    print()
    print("3. Crea el bucket:")
    print(f"   gsutil mb -p {project_id} -c STANDARD -l US gs://{bucket_name}")
    print()
    print("4. Configura permisos uniformes (recomendado):")
    print(f"   gsutil uniformbucketlevelaccess set on gs://{bucket_name}")
    print()
    
    print("OPCIÓN 2: Usando la consola de GCP")
    print("-" * 80)
    print()
    print("1. Ve a la consola de Cloud Storage:")
    print(f"   https://console.cloud.google.com/storage/browser?project={project_id}")
    print()
    print("2. Haz clic en 'CREATE BUCKET'")
    print()
    print("3. Configura:")
    print(f"   • Name: {bucket_name}")
    print("   • Location type: Region")
    print("   • Location: us-central1 (o tu región preferida)")
    print("   • Storage class: Standard")
    print("   • Access control: Uniform")
    print("   • Protection tools: None (o según necesites)")
    print()
    print("4. Haz clic en 'CREATE'")
    print()
    
    print("OPCIÓN 3: Usando Python (este script)")
    print("-" * 80)
    print()
    print("Puedes agregar la opción --create para crear el bucket automáticamente:")
    print(f"   python backend/validate_gcs_bucket.py --create")
    print()


def create_bucket_if_needed():
    """
    Crea el bucket si no existe (requiere confirmación del usuario).
    """
    bucket_name = settings.GCS_BUCKET_NAME
    project_id = settings.GOOGLE_CLOUD_PROJECT
    
    print(f"⚠️  ¿Deseas crear el bucket '{bucket_name}' en el proyecto '{project_id}'? (y/n): ", end="")
    response = input().strip().lower()
    
    if response != 'y':
        print("   Operación cancelada.")
        return False
    
    try:
        client = storage.Client(project=project_id)
        
        print(f"   • Creando bucket '{bucket_name}'...")
        bucket = client.create_bucket(
            bucket_name,
            location="US",
            predefined_acl=None,
            predefined_default_object_acl=None,
        )
        
        # Habilitar uniform bucket-level access
        bucket.iam_configuration.uniform_bucket_level_access_enabled = True
        bucket.patch()
        
        print(f"   ✅ Bucket '{bucket_name}' creado exitosamente")
        print(f"   • Location: {bucket.location}")
        print(f"   • Storage Class: {bucket.storage_class}")
        
        return True
        
    except exceptions.Conflict:
        print(f"   ⚠️  El bucket '{bucket_name}' ya existe")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR al crear bucket:")
        print(f"   {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Valida configuración de GCS')
    parser.add_argument('--create', action='store_true', 
                       help='Crear el bucket si no existe')
    parser.add_argument('--instructions', action='store_true',
                       help='Mostrar instrucciones de creación')
    
    args = parser.parse_args()
    
    if args.instructions:
        show_create_bucket_instructions()
        sys.exit(0)
    
    # Ejecutar validación
    success = validate_gcs_bucket()
    
    if not success and args.create:
        print()
        create_bucket_if_needed()
        print()
        print("Ejecutando validación nuevamente...")
        print()
        success = validate_gcs_bucket()
    
    if not success:
        print()
        print("💡 TIP: Ejecuta con --instructions para ver cómo crear el bucket")
        print("   python backend/validate_gcs_bucket.py --instructions")
        print()
        sys.exit(1)
    
    sys.exit(0)
