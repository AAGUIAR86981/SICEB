# Diccionario de Datos: Sistema Lider Pollo

Este documento describe la estructura, propósito y estado actual de la base de datos `maindata`.

## 1. Tablas de Catálogos (Tablas Maestras)
Estas tablas contienen la información base que se reutiliza en todo el sistema.

| Tabla | Propósito | Registros |
| :--- | :--- | :--- |
| `cat_departamentos` | Lista de departamentos oficiales de la empresa. | 25 |
| `cat_tipos_nomina` | Define las frecuencias de pago (Semanal, Quincenal). | 2 |
| `catalogo_productos` | Master de productos disponibles para provisiones. | 5 |
| `permissions` | Lista de acciones permitidas en el código (ej. `create_provisions`). | 5 |
| `roles` | Grupos de acceso (Administrador, Supervisor, Usuario). | 4 |

## 2. Tablas de Personal
| Tabla | Propósito | Registros |
| :--- | :--- | :--- |
| `empleados` | Información detallada de todos los trabajadores beneficiarios. | 116 |
| `empleadosaudit` | Historial de cambios realizados en los datos de empleados. | 1 |
| `users` | Cuentas de acceso al sistema para personal administrativo. | 5 |
| `user_roles` | Vincula a cada usuario con sus roles de acceso. | 5 |
| `role_permissions` | Define qué permisos tiene cada rol (RBAC). | 11 |

## 3. Tablas de Combos
| Tabla | Propósito | Registros |
| :--- | :--- | :--- |
| `combos` | Agrupaciones predefinidas de productos (ej. "Combo Semanal"). | 2 |
| `combo_items` | Relación de productos y cantidades que componen cada combo. | 10 |

## 4. Tablas de Provisiones (Operaciones)
| Tabla | Propósito | Registros |
| :--- | :--- | :--- |
| `provision_items` | Productos por defecto para provisiones estándar (sin combos). | 0 |
| `provisiones_historial` | Registro maestro de cada proceso de entrega realizado. | 1 |
| `provision_beneficiarios` | Registro individual de quién recibió o no el beneficio. | 0* |
| `provision_productos_historial` | Detalle de productos entregados en cada provisión histórica. | 0* |

> [!NOTE]
> Las tablas marcadas con `0*` se llenarán automáticamente en cada nuevo proceso de entrega.

## 5. Auditoría y Seguridad
| Tabla | Propósito | Registros |
| :--- | :--- | :--- |
| `user_activities` | Bitácora de acciones de seguridad (inicios de sesión, cambios clave). | 2 |

---
**Documento generado el:** 09/02/2026
**Base de Datos:** MariaDB / maindata
