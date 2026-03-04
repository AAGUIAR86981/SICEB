# Inicialización de Base de Datos SICEB

Este documento describe la estructura completa de la base de datos del Sistema de Control de Entrega de Beneficios (SICEB).

## Tablas del Sistema

### 1. Catálogos (3NF)

- **cat_departamentos**: Catálogo de departamentos de la empresa
- **cat_tipos_nomina**: Tipos de nómina (Semanal/Quincenal)
- **catalogo_productos**: Catálogo de productos para provisiones

### 2. Usuarios y Autenticación

- **users**: Usuarios del sistema
- **roles**: Roles de usuario (administrador, supervisor, etc.)
- **permissions**: Permisos del sistema
- **user_roles**: Relación usuarios-roles (muchos a muchos)
- **role_permissions**: Relación roles-permisos (muchos a muchos)

### 3. Empleados

- **empleados**: Información de empleados (normalizada a 3NF)
- **empleados_audit**: Auditoría de cambios en empleados

### 4. Combos

- **combos**: Combos de productos predefinidos
- **combo_items**: Items que componen cada combo

### 5. Provisiones

- **provision_items**: Items de cada configuración
- **provisiones_historial**: Historial de provisiones realizadas
- **provision_productos_historial**: Detalle de productos por provisión

### 6. Logs y Auditoría

- **prov_logs**: Logs de provisiones
- **prov_emp_logs**: Logs de empleados en provisiones
- **user_logs**: Logs de actividad de usuarios
- **user_activities**: Actividades de usuarios
- **punchlog**: Registro de entradas/salidas

### 7. Vistas

- **v_proximos_cumpleanos**: Vista de próximos cumpleaños (30 días)
- **v_resumen_auditoria**: Resumen de auditoría de cambios

## Uso del Script de Inicialización

### Inicializar Base de Datos Completa

```bash
python init_database.py
```

Este script:

1. ✅ Crea todas las 23 tablas con sus estructuras correctas
2. ✅ Establece índices y claves foráneas
3. ✅ Crea las vistas necesarias
4. ✅ Inserta datos iniciales (departamentos, tipos de nómina, productos básicos)

### Verificar Tablas Creadas

```python
import mariadb
from dotenv import load_dotenv
import os

load_dotenv()
conn = mariadb.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
cursor = conn.cursor()
cursor.execute('SHOW TABLES')
print([t[0] for t in cursor.fetchall()])
```

## Relaciones Importantes

### Empleados (3NF)

```
empleados
├── departamento_id → cat_departamentos.id
└── tipo_nomina_id → cat_tipos_nomina.id
```

### Combos

```
combos
└── combo_items
    ├── combo_id → combos.id
    └── producto_id → catalogo_productos.id
```

### Provisiones

```
provisiones_historial
└── provision_productos_historial
    └── provision_id → provisiones_historial.id
```

## Datos Iniciales

El script inserta automáticamente:

- **Departamentos**: Administración, RRHH, Producción, Logística, Ventas, Sistemas, Mantenimiento
- **Tipos de Nómina**: Semanal (ID=1), Quincenal (ID=2)
- **Productos**: Aceite, Arroz, Azúcar, Café, Harina, Pasta, Pollo Entero, Sal, Sardina

## Notas Importantes

1. **Charset**: Todas las tablas usan `utf8mb4` con `utf8mb4_bin` para soportar caracteres especiales
2. **Timestamps**: Se usan timestamps automáticos para auditoría
3. **Índices**: Se crean índices en campos frecuentemente consultados
4. **Cascadas**: Las relaciones tienen `ON DELETE CASCADE` donde corresponde
5. **3NF**: El sistema está completamente normalizado a Tercera Forma Normal
