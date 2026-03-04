# Estrategia de Redundancia y Backup de Alta Frecuencia

Para proteger el sistema `lider_pollo` contra daños en el servidor, existen dos niveles de solución. La ventaja es que ambas se configuran a **nivel de servidor de base de datos**, por lo que el código Python de tu proyecto NO necesita ser modificado ni se verá afectado.

---

## Opción 1: Replicación Maestro-Esclavo (En tiempo real)
Esta es la solución más profesional. En lugar de esperar 3 minutos, cualquier cambio en tu base de datos principal se copia **al instante** en una base de datos secundaria (puede ser en otro servidor o en el mismo).

### Cómo funciona:
1. El **Maestro** (tu DB actual) guarda un archivo llamado `Binary Log` con cada cambio.
2. El **Esclavo** (la copia) lee ese archivo constantemente y replica el cambio.

### Implementación (Referencia):
En el archivo de configuración de MariaDB/MySQL (`my.cnf` o `my.ini`):
```ini
# Configuración en el Maestro
server-id = 1
log-bin = mysql-bin
binlog-do-db = lider_pollo
```

---

## Opción 2: Backup Automatizado cada 3 minutos

Si prefieres copias de seguridad (archivos descargables), puedes programar una tarea en Windows (o un Cron en Linux) para ejecutar el comando `mysqldump`.

### El Script de Backup (`backup.bat` para Windows)
Crea un archivo llamado `generar_backup.vbs` o un `.bat` con este contenido:
```batch
@echo off
set FECHA=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set FECHA=%FECHA: =0%
"C:\Program Files\MariaDB 10.x\bin\mysqldump" -u root -ptu_password lider_pollo > C:\backups_lider_pollo\backup_%FECHA%.sql

-- Limpiar backups de más de 1 día para no llenar el disco
forfiles /p "C:\backups_lider_pollo" /s /m *.sql /d -1 /c "cmd /c del @path"
```

### Ejecución cada 3 minutos:
1. Abrir el **Programador de Tareas de Windows**.
2. Crear una tarea nueva que ejecute este script.
3. En la pestaña **Desencadenadores**, poner: "Repetir cada 3 minutos".

---

## Opción 3: Base de Datos de Espejo Local (Seguridad Sencilla)

Si solo quieres una segunda base de datos en el mismo servidor para "pruebas" o "salvaguarda rápida", puedes usar un Trigger que copie los datos de forma síncrona.

```sql
CREATE DATABASE lider_pollo_mirror;
-- (Importar esquema idéntico primero)

-- Trigger para cada tabla crítica (ejemplo empleados)
DELIMITER //
CREATE TRIGGER tr_mirror_empleados
AFTER INSERT ON lider_pollo.empleados
FOR EACH ROW
BEGIN
    INSERT INTO lider_pollo_mirror.empleados VALUES (NEW.*);
END; //
DELIMITER ;
```

---

## Recomendación de Arquitectura

| Nivel de Riesgo | Solución Recomendada | Ventaja |
| :--- | :--- | :--- |
| **Bajo** (Error borrar datos) | Triggers a DB Mirror | Instantáneo y local. |
| **Medio** (Servidor se apaga) | Backup 3 min a Nube | Tienes un archivo en Drive/Dropbox cada 3 min. |
| **Alto** (Disco se quema) | Replicación a otro Servidor | El sistema sigue funcionando en el segundo servidor ante un desastre. |

---

> [!IMPORTANT]
> **Consejo de Oro**: No guardes los backups en el mismo disco duro donde está la base de datos. Si el servidor se daña físicamente, perderás el original Y la copia. Usa una ruta de red o sincroniza la carpeta de backups con servicios como **OneDrive** o **Mega**.

> [!NOTE]
> Al realizar estos procesos, el sistema `lider_pollo` no se entera de que existe una copia, por lo que su rendimiento e integridad permanecen intactos.
