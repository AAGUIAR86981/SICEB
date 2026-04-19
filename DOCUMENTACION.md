# Documentación del Proyecto: Lider Pollo

## 1. Descripción General

El sistema **Lider Pollo** es una aplicación web desarrollada para gestionar la entrega de "provisiones" (beneficios de alimentación o productos) a los empleados de una organización. Permite el control de inventario, validación de entregas, reportes históricos y gestión de usuarios con permisos granulares.

---

## 2. Tecnologías Utilizadas

- **Backend**: Python 3.x con [Flask](https://flask.palletsprojects.com/).
- **Base de Datos**: [MariaDB](https://mariadb.org/) (usando el conector `mariadb`).
- **Seguridad**: `passlib` (PBKDF2-SHA256) para hashing de contraseñas y `python-dotenv` para gestión de secretos.
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla) y Jinja2 como motor de plantillas.

---

## 3. Estructura del Proyecto

```text
lider_pollo/
├── app.py                  # Punto de entrada de la aplicación
├── config/                 # Configuración de BD y constantes
├── controllers/            # Lógica de las rutas (Blueprints: auth, admin, provision, etc.)
├── models/                 # Lógica de acceso a datos y esquemas
├── static/                 # Archivos estáticos (CSS, JS, Imágenes)
├── templates/              # Plantillas Jinja2 (HTML)
├── utils/                  # Funciones auxiliares y decoradores de permisos
└── setup_advanced_db.py    # Scripts de inicialización avanzada (Vistas, Triggers)
```

---

## 4. Base de Datos

El sistema utiliza una base de datos relacional orientada a la integridad y auditoría.

### Tablas Principales

- **`users`**: Almacena usuarios del sistema (administradores y operadores).
- **`empleados`**: Información detallada del personal, incluyendo cédula, departamento y fecha de nacimiento.
- **`provisiones_historial`**: Registro de cada ciclo de entrega de productos.
- **`prov_emp_logs`**: Vinculación individual de entregas por empleado con validación (`boolValidacion`).
- **`roles` / `permissions`**: Tablas para el sistema de Control de Acceso Basado en Roles (RBAC).

### Características Avanzadas

- **Vistas**:
  - `v_proximos_cumpleanos`: Muestra los empleados que cumplen años en los próximos 7 días.
  - `v_resumen_auditoria`: Consolida los cambios realizados en los datos de empleados.
- **Triggers**: Sistema automático de auditoría para cambios en datos sensibles.

> [!TIP]
> Para un detalle exhaustivo de tablas, tipos de datos y diagramas ER, consulta la [Documentación Detallada de Base de Datos](file:///c:/Users/Admin/Documents/lider_pollo/DB_DOCUMENTACION.md).

---

## 5. Funcionalidades Principales

### Autenticación y RBAC

El sistema no solo permite el login de usuarios, sino que gestiona permisos específicos por módulo. Un usuario puede tener múltiples roles, y cada rol tiene un set de permisos definido en la BD.

### Ciclo de Provisiones

1. **Configuración**: Se define qué productos se entregarán y la frecuencia (semanal/quincenal).
2. **Validación**: Registro de la recepción por parte del empleado.
3. **Reportes**: Generación de logs para auditoría y control de existencias.

---

## 6. Configuración e Instalación

### Requisitos Previos

- Python 3.8+
- MariaDB Server

### Pasos

1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Configurar el archivo `.env` con las credenciales de tu base de datos:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=tu_password
   DB_NAME=lider_pollo
   SECRET_KEY=una_llave_secreta_muy_larga
   ```
5. Inicializar la base de datos: `python setup_advanced_db.py`.
6. Ejecutar la aplicación: `python app.py`.

---

## 7. Mantenimiento

Para actualizaciones del esquema o limpieza de datos, se disponen de scripts como `manage_db.py` y `update_schema_birthdays.py`.
