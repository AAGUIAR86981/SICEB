# Lider Pollo - Project Structure & Logic Report

**Generated on:** 2026-02-04
**Purpose:** Comprehensive guide for future updates and module integrations.

---

## 1. Directory Structure

```text
lider_pollo_dos/
├── app.py                  # Entry point (Main Application)
├── config/                 # Configuration & Database
├── controllers/            # Route logic (Blueprints)
├── models/                 # Data access layer & Business logic
├── static/                 # CSS, JS, Images
├── templates/              # HTML Templates (Jinja2)
├── utils/                  # Helpers & Decorators
└── venv/                   # Python Virtual Environment
```

---

## 2. Key Components Detailed

### A. Core Configuration (`config/`)
*   **`config/database.py`**:
    *   **Purpose**: Manages database connection and schema initialization.
    *   **Key Functions**:
        *   `get_db_connection()`: Connects to MariaDB. Creates DB if missing.
        *   `init_db_tables()`: Defines and creates all tables (`users`, `roles`, `permissions`, `provision_configs`, etc.). **Update this when adding new tables.**

### B. Models (`models/`)
Classes that handle direct interaction with the database.

*   **`models/user.py` (User Class)**
    *   **Functions**:
        *   `get_by_username(username)`: Fetch user metrics.
        *   `verify_credentials(username, password)`: Auth check.
        *   `get_user_roles(user_id)`: Fetches assigned roles.
        *   `get_user_permissions(role_ids)`: Fetches permissions (DB + Hardcoded fallback logic).
        *   `create(...)`: Creates new user.

*   **`models/provision.py` (Provision Class)**
    *   **Functions**:
        *   `get_type_and_week()`: Determines if current week is Semanal/Quincenal.
        *   `get_available_tables()`: Fetches active configs.
        *   `check_exists_today(tipo_nomina)`: **Validation** to prevent duplicates.
        *   `save_log(...)`: Records basic log of provision attempt.
        *   `save_history(...)`: Saves detailed JSON snapshot of the provision.

*   **`models/employee.py` (Employee Class)**
    *   **Functions**:
        *   `get_all(tipo_nomina, estado)`: Lists employees (active/invalid) for provision.
        *   `get_department_summary(...)`: Stats for charts/reports.

### C. Controllers (`controllers/`)
Flask Blueprints handling URL routes.

*   **`controllers/auth.py` (Blueprint: `auth`)**
    *   `@auth.route('/')`: Login page.
    *   `@auth.route('/access')`: Login processing (POST).
    *   `@auth.route('/admin/users')`: User management (CRUD).

*   **`controllers/provision.py` (Blueprint: `provision`)**
    *   `@provision.route('/provision')`: Main logic for generating provisions.
        *   *Uses `Provision.check_exists_today` validation.*
        *   *Uses `Employee.get_all` to fetch staff.*
    *   `@provision.route('/historial_provisiones')`: View past provisions.
    *   `@provision.route('/exportar/...')`: Excel/CSV export logic.

*   **`controllers/admin.py` (Blueprint: `admin`)**
    *   `@admin.route('/admin')`: Dashboard for creating users and viewing logs.

### D. Utilities (`utils/`)
*   **`utils/decorators.py`**:
    *   `@login_required`: Blocks unauthenticated access.
    *   `@admin_required`: Restricts to users with `isAdmin=1`.
    *   `@permission_required(code)`: Checks for specific permission codes (e.g., `'create_provisions'`).

---

## 3. Database Schema Overview

*   **Authentication**: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`.
*   **Business Data**:
    *   `empleados`: Master employee list.
    *   `provision_configs`: Configuration for weekly/bi-weekly baskets.
    *   `provision_items`: Products inside each config.
    *   `prov_logs`: Basic audit log of generated provisions.
    *   `provisiones_historial`: Detailed JSON storage of past provisions.

---

## 4. How to Integrate a New Module

To add a new feature (e.g., "Inventory"):

1.  **Model**: Create `models/inventory.py`.
    *   Define class `Inventory`.
    *   Add methods `get_items()`, `update_stock()`, etc.
2.  **Controller**: Create `controllers/inventory.py`.
    *   Define blueprint: `inventory_bp = Blueprint('inventory', __name__)`.
    *   Create routes: `@inventory_bp.route('/stock')`.
3.  **Register Blueprint**: In `app.py`:
    *   `from controllers.inventory import inventory_bp`
    *   `app.register_blueprint(inventory_bp)`
4.  **Permissions** (Optional but recommended):
    *   Add `manage_inventory` to `permissions` table.
    *   Assign to `administrador` role.
    *   Protect route with `@permission_required('manage_inventory')`.
5.  **Frontend**: Create `templates/inventory/index.html`.

---
**End of Report**
