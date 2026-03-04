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
├── controllers/            # Lógica de las rutas (Blueprints)
├── models/                 # Lógica de acceso a datos y modelos SQL
├── static/                 # Archivos estáticos (CSS, JS)
├── templates/              # Plantillas Jinja2 (HTML)
├── utils/                  # Funciones auxiliares y decoradores
└── init_database.py        # Script único de inicialización de BD
```

---

## 4. Base de Datos

El sistema utiliza una base de datos relacional orientada a la integridad y auditoría.

### Tablas Principales

- **`users`**: Gestión de acceso y roles.
- **`empleados`**: Registro maestro del personal y nómina.
- **`provisiones_historial`**: Histórico maestro de ciclos de entrega.
- **`combos`**: Definición de paquetes de productos.
- **`roles` / `permissions`**: Sistema RBAC granular.

### Características Avanzadas

- **Auditoría Automática**: Trigger `after_empleado_update` que registra cambios técnicos.
- **Reportes Dinámicos**: Vista `v_resumen_auditoria` para supervisión rápida.

> [!TIP]
> Para un detalle exhaustivo de tablas, tipos de datos y diagramas ER, consulta el [Diccionario de Datos Detallado](file:///c:/Users/Laptop/OneDrive/Documentos/lider_pollo/DB_DOCUMENTACION.md).

---

## 5. Funcionalidades Principales

### Autenticación y RBAC

El sistema gestiona permisos específicos por módulo. Los roles (Administrador, Supervisor, etc.) tienen permisos asignados que controlan la visibilidad de botones y acceso a rutas.

### Ciclo de Provisiones

1. **Configuración**: Definición de rubros por periodo.
2. **Validación**: Registro de aprobaciones de entrega.
3. **Historial**: Consulta de procesos pasados y descarga de reportes en Excel/CSV.

---

## 6. Configuración e Instalación

### Requisitos Previos

- Python 3.8+
- MariaDB Server

### Pasos

1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Configurar el archivo `.env` (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY).
5. Inicializar la base de datos: `python init_database.py`.
6. Ejecutar la aplicación: `python app.py`.

---

## 7. Mantenimiento

Toda la estructura se centraliza en `init_database.py`. Para tareas administrativas adicionales, se utilizan los scripts ubicados en la carpeta `scripts/`, tales como:
- `backup_database.py`: Respaldo programado de la base de datos.
- `restore_database.py`: Restauración de la base de datos desde un archivo SQL.
- `fix_permissions.py`: Ajuste de permisos de archivos.

