import mariadb
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "lider_pollo")
        )
        return connection
    except mariadb.Error as err:
        print(f"Error: {err}")
        return None

def check_normalization_and_integrity():
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    report = {
        "normalization": [],
        "integrity_issues": [],
        "stats": {}
    }
    
    # 1. Check if 'empleados.departamento' contains values not in 'cat_departamentos'
    cursor.execute("SELECT DISTINCT departamento FROM empleados WHERE departamento IS NOT NULL")
    emp_depts = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT nombre FROM cat_departamentos")
    cat_depts = {row[0] for row in cursor.fetchall()}
    
    missing_depts = emp_depts - cat_depts
    if missing_depts:
        report["normalization"].append({
            "issue": "Atomic values mismatch / Reference missing",
            "details": f"Employees table has departments not in cat_departamentos: {list(missing_depts)}",
            "table": "empleados"
        })
    else:
        report["normalization"].append({
            "status": "OK",
            "details": "All departments in 'empleados' match 'cat_departamentos' (standardized text)."
        })

    # 2. Check for missing FK constraints (informal check)
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (os.getenv("DB_NAME", "lider_pollo"),))
    fks = cursor.fetchall()
    fk_map = {(row[0], row[1]): row[2] for row in fks}
    
    needed_fks = [
        ("empleados", "tipoNomina", "cat_tipos_nomina"),
        ("empleados", "departamento", "cat_departamentos") # If it were INT
    ]
    
    for table, col, ref in needed_fks:
        if (table, col) not in fk_map:
            report["normalization"].append({
                "issue": "Missing Foreign Key Constraint",
                "details": f"Table '{table}' column '{col}' has no formal FK to '{ref}'",
                "table": table
            })

    # 3. Check for orphan records in combo_items
    cursor.execute("""
        SELECT ci.id, ci.combo_id 
        FROM combo_items ci 
        LEFT JOIN combos c ON ci.combo_id = c.id 
        WHERE c.id IS NULL
    """)
    orphans = cursor.fetchall()
    if orphans:
        report["integrity_issues"].append({
            "issue": "Orphan combo_items",
            "count": len(orphans),
            "ids": [row[0] for row in orphans]
        })

    # 4. Check for redundant data in provision_beneficiarios
    # Redundancy check: can we match by ID and find different names/cedulas?
    # This is often intentional for snapshots, but good to know if they match current records.
    cursor.execute("""
        SELECT pb.id, pb.nombre_completo, e.nombre, e.apellido 
        FROM provision_beneficiarios pb
        JOIN empleados e ON pb.empleado_id = e.id
        WHERE pb.nombre_completo != CONCAT(e.nombre, ' ', e.apellido)
    """)
    mismatches = cursor.fetchall()
    if mismatches:
        report["normalization"].append({
            "info": "Snapshot mismatch (Likely Intentional)",
            "details": f"Found {len(mismatches)} records in provision_beneficiarios where name differs from current employee master.",
            "table": "provision_beneficiarios"
        })

    # 5. Get some stats
    tables = [
        "empleados", "users", "combos", "combo_items", "catalogo_productos", 
        "provisiones_historial", "provision_beneficiarios"
    ]
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            report["stats"][table] = cursor.fetchone()[0]
        except:
            report["stats"][table] = "Error or Table Missing"

    print(json.dumps(report, indent=4))
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_normalization_and_integrity()
