
from config.database import init_db_tables
from seed_data import seed_defaults
from seed_permissions import seed_permissions
import logging
import sys

# Configure logging to show info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def full_setup():
    print("="*50)
    print("      LIDER POLLO - FULL DATABASE SETUP")
    print("="*50)

    try:
        # 1. Create Tables
        print("\n1. Initializing Tables...")
        init_db_tables()
        print("   ✅ Tables initialized.")

        # 2. Seed Permissions (Important for RBAC)
        print("\n2. Seeding Permissions & Roles...")
        seed_permissions()
        # seed_permissions prints its own success format

        # 3. Seed Default Data (Provisions)
        print("\n3. Seeding Default Data (Provisions)...")
        seed_defaults()
        # seed_defaults prints its own success format

        print("\n" + "="*50)
        print("   ALL OPERATIONS COMPLETED SUCCESSFULLY")
        print("="*50)

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    full_setup()
