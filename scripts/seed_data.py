from config.database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_defaults():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        # Check if we have active configs
        cursor.execute("SELECT COUNT(*) FROM provision_configs WHERE active = 1 AND provision_type = 'semanal'")
        has_semanal = cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM provision_configs WHERE active = 1 AND provision_type = 'quincenal'")
        has_quincenal = cursor.fetchone()[0] > 0

        if not has_semanal:
            print("Seeding default Semanal config...")
            cursor.execute("INSERT INTO provision_configs (week_number, provision_type, active) VALUES ('1', 'semanal', 1)")
            config_id = cursor.lastrowid
            
            # Add default items
            items = [('Harina', 2), ('Arroz', 2), ('Pasta', 2), ('Azucar', 1), ('Aceite', 1)]
            for name, qty in items:
                cursor.execute("INSERT INTO provision_items (provision_config_id, product_name, quantity) VALUES (%s, %s, %s)", 
                             (config_id, name, qty))

        if not has_quincenal:
            print("Seeding default Quincenal config...")
            cursor.execute("INSERT INTO provision_configs (week_number, provision_type, active) VALUES ('1', 'quincenal', 1)")
            config_id = cursor.lastrowid
            
            # Add default items
            items = [('Pollo', 1), ('Carne', 1), ('Huevos', 1), ('Queso', 1), ('Mortadela', 1)]
            for name, qty in items:
                cursor.execute("INSERT INTO provision_items (provision_config_id, product_name, quantity) VALUES (%s, %s, %s)", 
                             (config_id, name, qty))

        conn.commit()
        print("✅ Seeding complete.")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_defaults()
