# Registro de Conexión, Auditoría Global e IP

Para lograr un control de seguridad 360°, la dirección IP debe integrarse en todas las capas del sistema. Aquí te detallo el esquema para los niveles de control:

---

## 1 y 2. Nivel: Inicios de Sesión y Actividades (**TABLA COMPARTIDA**)
He verificado tu código y, efectivamente, el "Histórico" que ves en pantalla y la tabla de "Actividades" **son la misma en la base de datos** (`user_activities`). El sistema simplemente filtra los que dicen "Inicio de sesión" para mostrártelos aparte.

Por lo tanto, una sola modificación protege ambas vistas:

### SQL de Modificación (Existente)
```sql
-- Esto añadirá la IP a CUALQUIER actividad, incluyendo los inicios de sesión.
ALTER TABLE user_activities 
ADD COLUMN ip_address VARCHAR(45) AFTER activity_type;
```

---

## 3. Nivel: Auditoría Profunda de Datos (**TABLA EXISTENTE**)
En la tabla donde se guardan los cambios de tus empleados (`empleadosaudit`).

### SQL de Integración (Existente)
```sql
ALTER TABLE empleadosaudit 
ADD COLUMN ip_address VARCHAR(45) AFTER changed_by;
```

---

## 4. Implementación Técnica (Referencia Flask)

Para que el sistema capture la IP automáticamente al iniciar sesión y al hacer cualquier cambio:

### Captura Centralizada en Python:
```python
# En utils/helpers.py
def get_client_ip():
    from flask import request
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def log_user_activity(user_id, username, activity_type, activity_details):
    ip = get_client_ip()
    # Ahora el INSERT incluirá el nuevo campo 'ip'
    cursor.execute(
        'INSERT INTO user_activities (user_id, username, activity_type, activity_details, ip_address) VALUES (%s, %s, %s, %s, %s)',
        (user_id, username, activity_type, activity_details, ip)
    )
```

---

## 5. Resumen de Flujo de Seguridad

| Capa | Momento | Objetivo |
| :--- | :--- | :--- |
| **Activities (Shared)** | Al loguearse o navegar. | Auditar el origen físico de cada acción o entrada. |
| **Data Audit** | Al modificar registros clave (SQL). | Prueba legal e inmutable de quién cambió un dato y desde dónde. |

---

> [!IMPORTANT]
> **Privacidad y Legalidad**: Al registrar la IP en todos los niveles, los reportes de auditoría serán extremadamente precisos. Asegúrese de que el acceso a estas tablas esté restringido únicamente a usuarios con el permiso de "Auditor de Seguridad".

> [!TIP]
> **Consolidación**: Si decides usar la opción de **Base de Datos Externa** (que vimos anteriormente), puedes mover estas tablas a esa base de datos privada para mantener la operativa (`lider_pollo`) lo más ligera y rápida posible.
