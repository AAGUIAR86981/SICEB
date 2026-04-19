from models.employee import Employee
from config.database import get_db_connection

def check_logic():
    print("Checking Employee.get_all('1', 'inactivo')...") # Semanal
    invalidados_sem = Employee.get_all('1', 'inactivo', 1000)
    print(f"  Result count: {len(invalidados_sem)}")
    for e in invalidados_sem:
        print(f"  - {e}")

    print("\nChecking Employee.get_all('2', 'inactivo')...") # Quincenal
    invalidados_quin = Employee.get_all('2', 'inactivo', 1000)
    print(f"  Result count: {len(invalidados_quin)}")
    for e in invalidados_quin:
        print(f"  - {e}")

if __name__ == "__main__":
    check_logic()
