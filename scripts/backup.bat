@echo off
REM ========================================
REM   BACKUP DE BASE DE DATOS - LIDER POLLO
REM ========================================

echo.
echo Iniciando proceso de backup...
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0.."

REM Ejecutar script de Python
python scripts\backup_database.py

REM Verificar resultado
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✅ BACKUP COMPLETADO EXITOSAMENTE
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ❌ ERROR EN EL BACKUP
    echo ========================================
)

echo.
pause
