# Scripts de Backup y Restauración - Lider Pollo

Este directorio contiene scripts para realizar backups automáticos y restauración de la base de datos.

## 📁 Archivos

### Scripts de Backup
- **`backup_database.py`** - Script principal de backup (Python)
- **`backup.bat`** - Ejecutable de backup para Windows

### Scripts de Restauración
- **`restore_database.py`** - Script de restauración interactivo (Python)
- **`restore.bat`** - Ejecutable de restauración para Windows

### Automatización
- **`setup_scheduled_backup.ps1`** - Configura tarea programada en Windows

## 🚀 Uso Rápido

### Crear un Backup Manual

**Opción 1: Doble clic**
```
Doble clic en: backup.bat
```

**Opción 2: Línea de comandos**
```bash
cd C:\Users\Laptop\OneDrive\Documentos\lider_pollo
python scripts\backup_database.py
```

### Restaurar desde Backup

**Opción 1: Doble clic**
```
Doble clic en: restore.bat
```

**Opción 2: Línea de comandos**
```bash
cd C:\Users\Laptop\OneDrive\Documentos\lider_pollo
python scripts\restore_database.py
```

## ⏰ Configurar Backups Automáticos

### Paso 1: Ejecutar PowerShell como Administrador
1. Presiona `Win + X`
2. Selecciona "Windows PowerShell (Administrador)"

### Paso 2: Ejecutar el Script de Configuración
```powershell
cd C:\Users\Laptop\OneDrive\Documentos\lider_pollo
.\scripts\setup_scheduled_backup.ps1
```

Esto creará una tarea programada que ejecutará backups automáticamente todos los días a las 2:00 AM.

### Verificar la Tarea Programada
1. Presiona `Win + R`
2. Escribe: `taskschd.msc`
3. Busca: "Backup Lider Pollo Diario"

## 📊 Características

### Backup Automático
- ✅ Crea backups con timestamp (fecha y hora)
- ✅ Mantiene automáticamente los últimos 30 backups
- ✅ Elimina backups antiguos automáticamente
- ✅ Incluye todas las tablas, triggers, rutinas y eventos
- ✅ Muestra tamaño del archivo creado

### Restauración Interactiva
- ✅ Lista todos los backups disponibles
- ✅ Muestra fecha y tamaño de cada backup
- ✅ Confirmación de seguridad antes de restaurar
- ✅ Advertencias claras sobre sobrescritura de datos

## 📦 Ubicación de Backups

Los backups se guardan en:
```
C:\Users\Laptop\OneDrive\Documentos\lider_pollo\backups\
```

Formato de nombre:
```
backup_lider_pollo_db_YYYYMMDD_HHMMSS.sql
```

Ejemplo:
```
backup_lider_pollo_db_20260206_020000.sql
```

## ⚠️ Requisitos

### Software Necesario
- Python 3.8 o superior
- MariaDB o MySQL instalado
- `mysqldump` y `mysql` en el PATH del sistema

### Verificar Instalación
```bash
# Verificar Python
python --version

# Verificar mysqldump
mysqldump --version

# Verificar mysql
mysql --version
```

### Agregar MySQL/MariaDB al PATH

Si `mysqldump` no se reconoce:

1. Busca la carpeta de instalación de MariaDB:
   ```
   C:\Program Files\MariaDB 10.x\bin
   ```

2. Agregar al PATH:
   - Presiona `Win + Pause`
   - Clic en "Configuración avanzada del sistema"
   - Clic en "Variables de entorno"
   - En "Variables del sistema", busca "Path"
   - Clic en "Editar"
   - Clic en "Nuevo"
   - Pega: `C:\Program Files\MariaDB 10.x\bin`
   - Clic en "Aceptar" en todas las ventanas

3. Reinicia la terminal/PowerShell

## 🔒 Seguridad

### Proteger Backups
- Los backups contienen TODOS los datos de la base de datos
- Mantén los backups en un lugar seguro
- No compartas backups por medios inseguros
- Considera encriptar backups sensibles

### Archivo .env
El archivo `.env` contiene las credenciales de la base de datos:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=lider_pollo_db
```

**NUNCA** subas el archivo `.env` a repositorios públicos.

## 🆘 Solución de Problemas

### Error: "mysqldump no se reconoce como comando"
**Solución:** Agregar MariaDB al PATH (ver sección Requisitos)

### Error: "Access denied for user"
**Solución:** Verificar credenciales en el archivo `.env`

### Error: "Can't connect to MySQL server"
**Solución:** 
1. Verificar que MariaDB esté corriendo
2. Verificar `DB_HOST` y `DB_PORT` en `.env`

### Backup muy grande
**Solución:** Los backups se comprimen automáticamente después de 30 días

## 📞 Soporte

Para más información, consulta la guía completa:
```
C:\Users\Laptop\.gemini\antigravity\brain\...\guia_backup_restauracion.md
```

## 📝 Notas

- Los backups se ejecutan con `--single-transaction` para no bloquear la BD
- Se incluyen triggers, rutinas y eventos automáticamente
- La restauración requiere confirmación explícita para evitar pérdida de datos
- Los backups antiguos se eliminan automáticamente (mantiene últimos 30)
