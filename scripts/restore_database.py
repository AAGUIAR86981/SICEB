"""
Script de Restauración de Base de Datos
Permite restaurar la base de datos desde un backup
Muestra lista de backups disponibles para seleccionar
"""

import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Directorio de backups
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")

def list_backups():
    """Lista todos los backups disponibles ordenados por fecha"""
    
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = [
        f for f in os.listdir(BACKUP_DIR) 
        if f.startswith("backup_") and f.endswith(".sql")
    ]
    
    # Ordenar por fecha (más recientes primero)
    backups.sort(reverse=True)
    
    return backups

def get_backup_info(backup_file):
    """Obtiene información de un archivo de backup"""
    
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    if not os.path.exists(backup_path):
        return None
    
    # Tamaño del archivo
    size_bytes = os.path.getsize(backup_path)
    size_mb = size_bytes / (1024 * 1024)
    
    # Fecha de modificación
    timestamp = os.path.getmtime(backup_path)
    date = datetime.fromtimestamp(timestamp)
    
    return {
        'file': backup_file,
        'path': backup_path,
        'size_mb': size_mb,
        'size_bytes': size_bytes,
        'date': date
    }

def restore_backup(backup_file):
    """Restaura la base de datos desde un backup"""
    
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    if not os.path.exists(backup_path):
        print(f"❌ Error: Archivo no encontrado: {backup_file}")
        return False
    
    # Validar configuración
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        print("❌ Error: Faltan variables de entorno (DB_USER, DB_PASSWORD, DB_NAME)")
        return False
    
    print()
    print("⚠️" * 30)
    print("⚠️  ADVERTENCIA: OPERACIÓN DESTRUCTIVA")
    print("⚠️" * 30)
    print()
    print(f"Esta operación SOBRESCRIBIRÁ completamente la base de datos '{DB_NAME}'")
    print(f"con los datos del backup: {backup_file}")
    print()
    print("⚠️  TODOS LOS DATOS ACTUALES SE PERDERÁN")
    print()
    
    confirm = input("¿Estás ABSOLUTAMENTE seguro? (escribe 'SI' en mayúsculas para continuar): ")
    
    if confirm != 'SI':
        print()
        print("❌ Restauración cancelada por el usuario")
        return False
    
    print()
    print(f"🔄 Restaurando desde: {backup_file}...")
    print(f"📁 Origen: {backup_path}")
    
    # Comando mysql
    cmd = [
        "mysql",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}"
    ]
    
    try:
        # Ejecutar restauración
        with open(backup_path, 'r', encoding='utf8') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=True,
                text=True
            )
        
        print()
        print("✅ Base de datos restaurada exitosamente")
        print(f"📊 Base de datos: {DB_NAME}")
        print(f"🕐 Fecha del backup: {get_backup_info(backup_file)['date'].strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        print()
        print(f"❌ Error al restaurar backup: {error_msg}")
        return False
    
    except FileNotFoundError:
        print()
        print("❌ Error: 'mysql' no encontrado")
        print("💡 Asegúrate de que MariaDB/MySQL esté instalado y en el PATH")
        print("💡 Ubicación típica: C:\\Program Files\\MariaDB 10.x\\bin")
        return False
    
    except Exception as e:
        print()
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    
    print("=" * 60)
    print("  RESTAURACIÓN DE BASE DE DATOS - LIDER POLLO")
    print("=" * 60)
    print()
    
    # Listar backups disponibles
    backups = list_backups()
    
    if not backups:
        print("❌ No hay backups disponibles en el directorio:")
        print(f"   {BACKUP_DIR}")
        print()
        print("💡 Primero crea un backup ejecutando: python scripts\\backup_database.py")
        return 1
    
    print(f"📁 Directorio de backups: {BACKUP_DIR}")
    print(f"📊 Backups disponibles: {len(backups)}")
    print()
    print("Selecciona el backup a restaurar:")
    print()
    
    # Mostrar lista de backups
    for i, backup in enumerate(backups, 1):
        info = get_backup_info(backup)
        if info:
            print(f"  {i}. {info['file']}")
            print(f"     📅 Fecha: {info['date'].strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"     📦 Tamaño: {info['size_mb']:.2f} MB")
            print()
    
    print(f"  0. ❌ Cancelar")
    print()
    
    # Solicitar selección
    try:
        choice = input("Ingresa el número del backup (0 para cancelar): ").strip()
        choice = int(choice)
        
        if choice == 0:
            print()
            print("❌ Operación cancelada por el usuario")
            return 0
        
        if 1 <= choice <= len(backups):
            selected_backup = backups[choice - 1]
            success = restore_backup(selected_backup)
            return 0 if success else 1
        else:
            print()
            print("❌ Opción inválida")
            return 1
            
    except ValueError:
        print()
        print("❌ Entrada inválida. Debes ingresar un número.")
        return 1
    
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Operación cancelada por el usuario (Ctrl+C)")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print()
        print("=" * 60)
        sys.exit(exit_code)
    except Exception as e:
        print()
        print(f"❌ Error fatal: {e}")
        print("=" * 60)
        sys.exit(1)
