from config.database import get_db_connection
from models.user import User
from models.provision import Provision
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging to console
logging.basicConfig(level=logging.INFO)

def verify_auth():
    print("\n--- Verifying Auth ---")
    try:
        user = User.get_by_username('admin')
        if not user:
            print("  Admin user not found")
            return

        print(f"  User found: {user.username} (ID: {user.id})")

        roles, role_ids = User.get_user_roles(user.id)
        print(f"Roles: {roles}")
        
        if 'administrador' in roles:
            print("  Admin has 'administrador' role")
        else:
            print("  Admin MISSING 'administrador' role")

        permissions = User.get_user_permissions(role_ids, user.is_admin)
        print(f"Permissions count: {len(permissions)}")

        # Verify Supervisor Role Logic
        print("\n--- Verifying Supervisor Logic ---")
        try:
            # Mock or check logic directly if we can't switch user easily
            # We can use the static method with a mock set of role IDs if we knew the ID for supervisor
            # Let's fetch the ID for supervisor
            cursor = get_db_connection().cursor()
            cursor.execute("SELECT id FROM roles WHERE name='supervisor'")
            row = cursor.fetchone()
            if row:
                sup_id = row[0]
                sup_perms = User.get_user_permissions([sup_id], False)
                print(f"Supervisor Permissions: {len(sup_perms)}")
                if 'create_provisions' in sup_perms:
                    print("  Supervisor HAS 'create_provisions'")
                else:
                    print("  Supervisor MISSING 'create_provisions'")
            else:
                 print("  Supervisor role not found in DB")
            cursor.close()
            
        except Exception as e:
             print(f"  Supervisor check failed: {e}")

    except Exception as e:
        print(f"  Auth verification failed: {e}")

def verify_provisions():
    print("\n--- Verifying Provisions ---")
    try:
        config_semanal, config_quincenal = Provision.get_available_tables()
        
        if config_semanal:
            print(f"  Config Semanal found: ID {config_semanal['id']} - Week {config_semanal['week_number']}")
            products = Provision.get_products(config_semanal['id'], 0)
            print(f"   Products count: {len(products)}")
            if len(products) > 0:
                print(f"   Sample: {products[0]}")
        else:
            print("  Config Semanal NOT found")

        if config_quincenal:
            print(f"  Config Quincenal found: ID {config_quincenal['id']} - Week {config_quincenal['week_number']}")
            products = Provision.get_products(config_quincenal['id'], 0)
            print(f"   Products count: {len(products)}")
        else:
            print("  Config Quincenal NOT found")

    except Exception as e:
        print(f"  Provision verification failed: {e}")

if __name__ == "__main__":
    verify_auth()
    verify_provisions()
