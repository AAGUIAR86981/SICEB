# Manual Técnico del Sistema: Lider Pollo

Este documento proporciona una guía técnica profunda sobre la arquitectura, el flujo de datos y el funcionamiento interno de cada módulo del sistema.

---

## 1. Arquitectura del Sistema

El sistema sigue el patrón **MVC (Modelo-Vista-Controlador)** simplificado, adaptado para Flask:

- **Entry Point (`app.py`)**: Centraliza la inicialización de Flask, el registro de Blueprints y la configuración de seguridad (CORS, Sessions).
- **Controladores (`controllers/`)**: Implementan la lógica de negocio y las rutas. Utilizan Blueprints para modularizar la aplicación.
- **Modelos (`models/`)**: Clases y métodos estáticos que abstraen las consultas SQL. No utilizan un ORM pesado (como SQLAlchemy) para mantener el rendimiento y control total sobre las consultas.
- **Utilidades (`utils/`)**: Contiene decoradores críticos como `@login_required` y `@permission_required` que protegen las rutas mediante el sistema RBAC.

---

## 2. Sistema de Seguridad y RBAC

La seguridad se basa en tres pilares:

### 2.1 Autenticación (`auth.py`)
- **Hashing**: Uso de PBKDF2 via `passlib` para contraseñas.
- **Sesiones**: Manejo de sesiones encriptadas con Flask-Session.
- **Flujo**: El login valida credenciales, carga los permisos del usuario en la sesión (`session['user_permissions']`) y establece `session['isAdmin']` para accesos rápidos.

### 2.2 Control de Acceso Basado en Roles (RBAC)
Los permisos son granulares. Ejemplo de flujo:
1. Un usuario intenta acceder a `/crear_provision`.
2. El decorador `@permission_required('create_provisions')` verifica si ese permiso existe en la lista de la sesión del usuario.
3. **Carga de Permisos**: Al iniciar sesión, el sistema consulta `User.get_user_permissions`. Si la base de datos no tiene permisos definidos, el controlador `auth.py` aplica un *fallback* manual basado en el nombre del rol (Administrador tiene `all`, Supervisor tiene `create_provisions`, etc.).

---

## 3. Módulo de Gestión de Personal (`employees.py`)

Gestiona el recurso más crítico: los empleados.
- **Modelo (`models/employee.py`)**: Implementa búsquedas con filtros dinámicos (nombre, cédula, departamento) y paginación mediante `LIMIT` y `OFFSET`.
- **Auditoría Técnica (Triggers)**: Existe un disparador llamado `after_empleado_update` que se ejecuta después de cada `UPDATE`. Compara `OLD` vs `NEW` para los campos: `nombre`, `apellido`, `departamento`, `cedula` y `tipoNomina`, insertando automáticamente un registro en `empleadosaudit`.
- **Validación de Elegibilidad**: El campo `boolValidacion` es una bandera booleana. Solo los empleados con valor `1` son procesados durante la generación automática de provisiones.

---

## 4. Módulo de Combos y Productos (`products.py`, `combos.py`)

### 4.1 Catálogo de Productos
Maestro de rubros (`catalogo_productos`) que define qué se puede entregar. Categoriza productos en víveres, proteínas, etc.

### 4.2 Gestión de Combos
Estructura de paquetes predefinidos:
- **Combos**: Cabecera con nombre y descripción.
- **Combo Items**: Relación N:M que vincula productos específicos con una cantidad fija para ese combo.

---

## 5. El Corazón: Módulo de Provisiones (`provision.py`)

Este módulo orquesta el proceso estrella del sistema.

### 5.1 Flujo de Ejecución y Persistencia
1. **Selección de Periodo**: Se determina si es Semana ISO o Quincena.
2. **Procesamiento**: Se seleccionan empleados activos filtrados por `tipoNomina`.
3. **Registro de Historia**: 
   - Se crea una entrada en `provisiones_historial`.
   - Se guarda el desglose en `provision_productos_historial`.
   - Se almacena un JSON completo (`datos_completos`) con estadísticas del momento para garantizar que el reporte sea inalterable aunque los datos del empleado cambien en el futuro.

### 5.2 Exportación de Resultados
Utiliza `openpyxl` para generar archivos `.xlsx` profesionales. Los datos se extraen mapeando las claves del diccionario (`cedula`, `nombre`, etc.) para asegurar que las columnas coincidan con las expectativas del usuario.

---

## 6. Administración y Monitoreo (`admin.py`)

- **Logs de Actividad (`user_activities`)**: No solo registra errores, sino cada acción administrativa importante.
- **Vista `v_resumen_auditoria`**: Una vista SQL que agrupa los cambios por empleado, permitiendo ver de un vistazo quién es el personal con más modificaciones en su ficha.

---

## 7. Mantenimiento y Base de Datos

### 7.1 Inicialización e Idempotencia
`init_database.py` asegura la integridad del esquema. Utiliza `utf8mb4_bin` para las comparaciones de texto, lo que garantiza que las búsquedas sean precisas y sensibles a mayúsculas si es necesario.

### 7.2 Gestión de Conexiones
El pool de conexiones configurado en `config/database.py` es consumido por todos los modelos. Es vital llamar a `cursor.close()` y `conn.close()` (o usar bloques `try...finally`) para no saturar el servidor MariaDB.
