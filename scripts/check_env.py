
import os
from dotenv import load_dotenv
import sys

print("Current CWD:", os.getcwd())
print("Files in CWD:", os.listdir('.'))

load_dotenv()

print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))
password = os.getenv("DB_PASSWORD")
print("DB_PASSWORD:", "*****" if password else "None")

try:
    import mariadb
    print("MariaDB module imported successfully")
except ImportError as e:
    print("Error importing mariadb:", e)
