"""
Script de Backup Mejorado con Detección Automática de MariaDB
Busca automáticamente la instalación de MariaDB/MySQL
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import glob

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Directorio de backups (relativo al script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")

# Crear directorio si no existe
os.makedirs(BACKUP_DIR, exist_ok=True)

def find_mysqldump():
    """Busca mysqldump en ubicaciones comunes de Windows"""
    
    # Primero intentar desde PATH
    try:
        result = subprocess.run(
            ["where", "mysqldump"],
            capture_output=True,
            text=True,
            check=True
        )
        mysqldump_path = result.stdout.strip().split('\n')[0]
        if os.path.exists(mysqldump_path):
            return mysqldump_path
    except:
        pass
    
    # Buscar en ubicaciones comunes
    common_paths = [
        r"C:\Program Files\MariaDB*\bin\mysqldump.exe",
        r"C:\Program Files (x86)\MariaDB*\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Server*\bin\mysqldump.exe",
        r"C:\xampp\mysql\bin\mysqldump.exe",
        r"C:\wamp\bin\mysql\mysql*\bin\mysqldump.exe",
    ]
    
    for pattern in common_paths:
        matches = glob.glob(pattern)
        if matches:
            # Ordenar para obtener la versión más reciente
            matches.sort(reverse=True)
            return matches[0]
    
    return None

def create_backup():
    """Crea un backup de la base de datos"""
    
    # Validar configuración
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        print("❌ Error: Faltan variables de entorno (DB_USER, DB_PASSWORD, DB_NAME)")
        print("💡 Verifica el archivo .env en la raíz del proyecto")
        return False
    
    # Buscar mysqldump
    mysqldump_path = find_mysqldump()
    
    if not mysqldump_path:
        print("❌ Error: No se encontró 'mysqldump'")
        print()
        print("💡 Soluciones posibles:")
        print("   1. Instalar MariaDB desde: https://mariadb.org/download/")
        print("   2. Agregar MariaDB al PATH de Windows:")
        print("      - Ubicación típica: C:\\Program Files\\MariaDB 10.x\\bin")
        print("      - Win + Pause → Configuración avanzada → Variables de entorno")
        print("      - Editar 'Path' → Agregar la ruta de MariaDB")
        return False
    
    print(f"✅ mysqldump encontrado: {mysqldump_path}")
    
    # Nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.sql")
    
    # Comando mysqldump
    cmd = [
        mysqldump_path,
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--events",
        "--add-drop-database",
        "--databases",
        DB_NAME
    ]
    
    print(f"🔄 Iniciando backup de '{DB_NAME}'...")
    print(f"📁 Destino: {backup_file}")
    
    try:
        # Ejecutar mysqldump
        with open(backup_file, 'w', encoding='utf8') as f:
            result = subprocess.run(
                cmd, 
                stdout=f, 
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
        
        # Verificar que el archivo se creó correctamente
        if os.path.exists(backup_file):
            size_bytes = os.path.getsize(backup_file)
            size_mb = size_bytes / (1024 * 1024)
            
            print(f"✅ Backup completado exitosamente")
            print(f"📦 Tamaño: {size_mb:.2f} MB ({size_bytes:,} bytes)")
            print(f"📄 Archivo: {os.path.basename(backup_file)}")
            
            return True
        else:
            print("❌ Error: El archivo de backup no se creó")
            return False
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        print(f"❌ Error al crear backup: {error_msg}")
        
        # Eliminar archivo parcial si existe
        if os.path.exists(backup_file):
            os.remove(backup_file)
            print("🗑️ Archivo parcial eliminado")
        
        return False
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def cleanup_old_backups(keep=30):
    """Elimina backups antiguos, mantiene los últimos 'keep' archivos"""
    
    try:
        # Listar todos los backups
        backups = [
            f for f in os.listdir(BACKUP_DIR) 
            if f.startswith("backup_") and f.endswith(".sql")
        ]
        
        if len(backups) <= keep:
            print(f"📊 Total de backups: {len(backups)} (límite: {keep})")
            return
        
        # Ordenar por fecha (más recientes primero)
        backups.sort(reverse=True)
        
        # Eliminar los más antiguos
        deleted_count = 0
        for old_backup in backups[keep:]:
            old_path = os.path.join(BACKUP_DIR, old_backup)
            try:
                os.remove(old_path)
                deleted_count += 1
                print(f"🗑️ Eliminado: {old_backup}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {old_backup}: {e}")
        
        print(f"📊 Backups actuales: {len(backups) - deleted_count} (eliminados: {deleted_count})")
        
    except Exception as e:
        print(f"⚠️ Error en limpieza de backups: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("  BACKUP AUTOMÁTICO DE BASE DE DATOS - LIDER POLLO")
    print("=" * 60)
    print()
    
    # Crear backup
    success = create_backup()
    
    if success:
        print()
        print("🧹 Limpiando backups antiguos...")
        cleanup_old_backups(keep=30)
    
    print()
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
