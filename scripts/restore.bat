@echo off
REM ========================================
REM   RESTAURACIÓN DE BASE DE DATOS
REM ========================================

echo.
echo ⚠️  ADVERTENCIA: Esta operación sobrescribirá la base de datos actual
echo.
echo Iniciando proceso de restauración...
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0.."

REM Ejecutar script de Python
python scripts\restore_database.py

REM Verificar resultado
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✅ RESTAURACIÓN COMPLETADA
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ❌ ERROR EN LA RESTAURACIÓN
    echo ========================================
)

echo.
pause
