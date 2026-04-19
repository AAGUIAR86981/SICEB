# mostrar_estructura.py
import os
from pathlib import Path

def list_files(startpath, extensions=['.py', '.html', '.css', '.js', '.sql', '.txt']):
    for root, dirs, files in os.walk(startpath):
        # Ignorar carpetas
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', 'env', '.git', 'node_modules']]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}📁 {os.path.basename(root)}/')
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                print(f'{subindent}📄 {file}')

if __name__ == "__main__":
    print(f"📁 Estructura de: {os.getcwd()}\n")
    list_files(".")