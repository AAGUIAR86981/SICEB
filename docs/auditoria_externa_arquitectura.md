# Arquitectura de Auditoría en Base de Datos Externa

Es totalmente posible y, de hecho, es una **mejor práctica de seguridad** separar los logs de auditoría de los datos operativos. Esto evita que un usuario con acceso a la base de datos principal pueda "borrar sus huellas" fácilmente.

---

## Concepto General
Tendremos dos bases de datos en el mismo servidor (o en servidores distintos):
1.  **`lider_pollo`**: Base de datos operativa (Empleados, Provisiones, etc.).
2.  **`lider_pollo_audit`**: Base de datos privada (Solo registros de auditoría y logs).

---

## Opción A: Implementación Directa en SQL (Cross-Database Triggers)
Si ambas bases de datos están en el mismo servidor MariaDB/MySQL, los Triggers pueden escribir directamente de una base de datos a otra. Es la opción más transparente para el código Python.

### Paso 1: Crear la Base de Datos Privada
```sql
CREATE DATABASE lider_pollo_audit;

-- Crear la tabla de auditoría en la nueva DB
CREATE TABLE lider_pollo_audit.empleados_audit_externo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE'),
    datos_anteriores JSON,
    datos_nuevos JSON,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Paso 2: Configurar el Trigger "Puente"
Este disparador se crea en la base de datos principal (`lider_pollo`) pero apunta a la de auditoría.

```sql
DELIMITER //
CREATE TRIGGER lider_pollo.tr_external_audit_update
AFTER UPDATE ON lider_pollo.empleados
FOR EACH ROW
BEGIN
    -- Insertar directamente en la otra base de datos
    INSERT INTO lider_pollo_audit.empleados_audit_externo 
    (employee_id, tipo_operacion, datos_anteriores, datos_nuevos, usuario_id)
    VALUES (OLD.id, 'UPDATE', 
            JSON_OBJECT('nombre', OLD.nombre, 'cedula', OLD.cedula), 
            JSON_OBJECT('nombre', NEW.nombre, 'cedula', NEW.cedula),
            @current_user_id); -- Usando una variable de sesión para el ID
END; //
DELIMITER ;
```

---

## Opción B: Implementación por Código (Multi-Conexión)
Si las bases de datos están en servidores físicos diferentes o quieres más control desde Python.

### Referencia de Configuración (`config/database.py`)
```python
# Crear una segunda función de conexión
def get_audit_db_connection():
    return mysql.connector.connect(
        host="servidor_audit_seguro",
        user="usuario_audit_privado",
        password="password_secreto",
        database="lider_pollo_audit"
    )
```

### Uso en el Modelo de Auditoría
```python
def log_activity_externo(activity_data):
    conn = get_audit_db_connection()
    cursor = conn.cursor()
    # Insertar en la base de datos externa...
    cursor.close()
    conn.close()
```

---

## Ventajas de la Separación de Bases de Datos

1.  **Privacidad de Usuarios**: Puedes crear un usuario de base de datos que solo tenga permisos sobre `lider_pollo` pero NO sobre `lider_pollo_audit`. Así, ni siquiera el programador del día a día podría ver los logs si no tiene la clave de la segunda DB.
2.  **Rendimiento**: La base de datos principal es más ligera porque no tiene que cargar con miles de registros de logs.
3.  **Seguridad de Forense**: En caso de un ataque a la DB principal, los registros de "quién hizo qué" están a salvo en una ubicación diferente.
4.  **Backups Diferentes**: Puedes hacer copias de seguridad cada hora de la auditoría y cada día de la operativa.

---

## Recomendación de Seguridad Final
Para que esto sea 100% efectivo:
*   Use un **usuario de base de datos diferente** para la base de datos de auditoría.
*   No muestre estos logs en ninguna pantalla del panel administrativo estándar; solo en una herramienta de administración interna o un panel de "Súper Seguridad".

> [!TIP]
> **Dato Extra**: En SQL, puedes referenciar tablas de otra DB simplemente usando el punto: `NombreDB.NombreTabla`. Esto hace que mover los datos sea tan simple como cambiar un nombre en tus Triggers.
