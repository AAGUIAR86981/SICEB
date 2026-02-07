from config.database import get_db_connection
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO permissions (name, code, module) VALUES ('Gestionar Combos', 'manage_combos', 'catalogos')")
    conn.commit()
    print('✓ Permission added')
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()
