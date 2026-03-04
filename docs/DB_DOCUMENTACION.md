# Documentación de Base de Datos - SICEB

## Descripción General
La base de datos `lider_pollo` gestiona el Sistema de Control de Entregas de Provisiones (SICEB). Está diseñada en MariaDB/MySQL y sigue un esquema relacional normalizado (3NF) para garantizar la integridad y eficiencia de los datos.

## Estructura de Tablas

### 1. Autenticación y Usuarios

#### `users`
Almacena la información de los usuarios del sistema.
- **id**: INT, PK, Auto Increment
- **username**: VARCHAR(50), Unique
- **email**: VARCHAR(255)
- **password**: VARCHAR(255) (Hash)
- **isAdmin**: TINYINT (0/1)
- **name**: VARCHAR(100)
- **lastname**: VARCHAR(100)
- **created_at**: TIMESTAMP
- **last_login**: TIMESTAMP, Nullable
- **activo**: BOOLEAN (TRUE/FALSE)

#### `roles`
Define los roles disponibles en el sistema.
- **id**: INT, PK, Auto Increment
- **name**: VARCHAR(50), Unique
- **description**: VARCHAR(255)

#### `permissions`
Define los permisos granulares.
- **id**: INT, PK, Auto Increment
- **name**: VARCHAR(100)
- **code**: VARCHAR(100), Unique
- **module**: VARCHAR(50)

#### `user_roles`
Tabla intermedia para asignar roles a usuarios (Muchos a Muchos).
- **user_id**: INT, FK -> users(id)
- **role_id**: INT, FK -> roles(id)
- **assigned_at**: TIMESTAMP

#### `role_permissions`
Tabla intermedia para asignar permisos a roles.
- **role_id**: INT, FK -> roles(id)
- **permission_id**: INT, FK -> permissions(id)

---

### 2. Catálogos

#### `cat_departamentos`
Catálogo de departamentos de la empresa.
- **id**: INT, PK, Auto Increment
- **nombre**: VARCHAR(100), Unique
- **activo**: BOOLEAN
- **created_at**: TIMESTAMP

#### `cat_tipos_nomina`
Catálogo de tipos de nómina (ej. Semanal, Quincenal).
- **id**: INT, PK, Auto Increment
- **nombre**: VARCHAR(50), Unique
- **descripcion**: VARCHAR(255)
- **activo**: BOOLEAN

#### `catalogo_productos`
Productos disponibles para provisiones.
- **id**: INT, PK, Auto Increment
- **nombre**: VARCHAR(100), Unique
- **categoria**: VARCHAR(50)
- **unidad**: VARCHAR(20)
- **activo**: BOOLEAN
- **created_at**: TIMESTAMP

---

### 3. Empleados

#### `empleados`
Información de los empleados beneficiarios. Normalizada a 3NF.
- **id**: INT, PK, Auto Increment
- **cedula**: INT
- **nombre**: VARCHAR(100)
- **apellido**: VARCHAR(100)
- **departamento**: VARCHAR(100) (Legacy/Redundante)
- **departamento_id**: INT, FK -> cat_departamentos(id)
- **tipoNomina**: INT (Legacy)
- **tipo_nomina_id**: INT, FK -> cat_tipos_nomina(id)
- **id_empleado**: INT
- **boolValidacion**: TINYINT
- **fecha_ingreso**: DATE
- **created_at**: TIMESTAMP
- **updated_at**: TIMESTAMP

---

### 4. Combos

#### `combos`
Definición de combos de productos.
- **id**: INT, PK, Auto Increment
- **nombre**: VARCHAR(100), Unique
- **descripcion**: TEXT
- **activo**: BOOLEAN
- **created_by**: INT, FK -> users(id)
- **created_at**: TIMESTAMP
- **updated_at**: TIMESTAMP

#### `combo_items`
Detalle de productos dentro de un combo.
- **id**: INT, PK, Auto Increment
- **combo_id**: INT, FK -> combos(id)
- **producto_id**: INT, FK -> catalogo_productos(id)
- **cantidad**: INT

---

### 5. Provisiones


#### `provisiones_historial`
Cabecera de provisiones generadas. Tabla central del módulo de provisiones.
- **id**: INT, PK, Auto Increment
- **tipo_provision**: VARCHAR(20) — `'semanal'` o `'quincenal'` (slug)
- **semana**: INT — Número de período. Para semanal: semana ISO (1–53). Para quincenal: `MES×10+Q` (ej: feb 2ª = `22`)
- **tipo_nomina**: VARCHAR(20) — `'Semanal'` o `'Quincenal'`
- **productos**: TEXT — JSON con los productos del combo
- **cant_aprobados**: INT
- **cant_rechazados**: INT
- **datos_completos**: LONGTEXT — JSON con resumen completo de la provisión
- **usuario_id**: INT, FK → users(id)
- **usuario_nombre**: VARCHAR(100)
- **ip_address**: VARCHAR(45) — IP del usuario que generó la provisión
- **fecha_creacion**: TIMESTAMP
- **anio_provision**: INT, `STORED GENERATED` calculado como `YEAR(fecha_creacion)`

**Índices:**
| Nombre | Tipo | Columnas | Propósito |
|---|---|---|---|
| `PRIMARY` | PK | `id` | Identificador único |
| `idx_fecha` | INDEX | `fecha_creacion` | Búsqueda por fecha |
| `idx_tipo_semana` | INDEX | `tipo_nomina, semana` | Búsqueda rápida |
| `idx_control_fraude` | **UNIQUE** | `anio_provision, tipo_nomina, tipo_provision, semana` | **Antifraude**: impide duplicados por año+nómina+período |

> [!NOTE]
> El UNIQUE `idx_control_fraude` fue actualizado el 2026-02-27 para incluir `anio_provision`. La versión anterior no incluía el año, causando colisiones entre quincenas del mismo número en distintos meses.

#### `provision_productos_historial`
Detalle de productos en una provisión histórica.
- **id**: INT, PK, Auto Increment
- **provision_id**: INT, FK -> provisiones_historial(id)
- **producto_nombre**: VARCHAR(100)
- **cantidad**: INT

#### `provision_beneficiarios`
Registro de entregas a empleados por provisión.
- **id**: INT, PK, Auto Increment
- **provision_id**: INT, FK -> provisiones_historial(id)
- **empleado_id**: INT, FK -> empleados(id)
- **cedula**: INT
- **nombre_completo**: VARCHAR(255)
- **departamento**: VARCHAR(100)
- **recibio**: BOOLEAN
- **fecha_entrega**: TIMESTAMP

---

### 6. Auditoría

#### `user_activities`
Log de actividades de usuarios.
- **id**: INT, PK, Auto Increment
- **user_id**: INT
- **username**: VARCHAR(100)
- **activity_type**: VARCHAR(50)
- **activity_details**: TEXT
- **activity_date**: TIMESTAMP

#### `empleadosaudit`
Auditoría de cambios en datos de empleados.
- **id**: INT, PK, Auto Increment
- **employee_id**: INT, FK -> empleados(id)
- **field_name**: VARCHAR(50)
- **old_value**: TEXT
- **new_value**: TEXT
- **changed_at**: TIMESTAMP
- **changed_by**: INT, FK -> users(id)

## Notas Adicionales
- La base de datos utiliza `utf8mb4_bin` para soporte completo de caracteres y sensibilidad a mayúsculas/minúsculas donde aplica.
- Se utilizan Triggers (`after_empleado_update`) para poblar automáticamente la tabla de auditoría de empleados.
- Las tablas de log (`user_activities`, `empleadosaudit`, `provisiones_historial`, `users`) tienen columna `ip_address`/`last_ip` para rastreo de IP.
- La columna `anio_provision` en `provisiones_historial` es una columna `STORED GENERATED` calculada automáticamente como `YEAR(fecha_creacion)`.

---
*Última actualización: 2026-02-27 — Se documentaron columnas ip_address, anio_provision y el UNIQUE constraint idx_control_fraude corregido.*
