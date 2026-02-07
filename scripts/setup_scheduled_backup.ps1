# ========================================
#   CONFIGURAR TAREA PROGRAMADA DE BACKUP
# ========================================
#
# IMPORTANTE: Ejecutar como Administrador
# Clic derecho en PowerShell -> "Ejecutar como administrador"
#

# Configuracion
$taskName = "Backup Lider Pollo Diario"
$projectPath = "C:\Users\Laptop\OneDrive\Documentos\lider_pollo"
$scriptPath = Join-Path $projectPath "scripts\backup.bat"

# Verificar que el script existe
if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: No se encontro el script de backup en:" -ForegroundColor Red
    Write-Host "   $scriptPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Asegurate de que la ruta del proyecto sea correcta" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR TAREA PROGRAMADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Nombre de la tarea: $taskName" -ForegroundColor White
Write-Host "Script: $scriptPath" -ForegroundColor White
Write-Host "Horario: Diario a las 2:00 AM" -ForegroundColor White
Write-Host ""

# Eliminar tarea existente si existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "La tarea '$taskName' ya existe. Eliminando..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Crear accion (ejecutar el script)
$action = New-ScheduledTaskAction `
    -Execute $scriptPath `
    -WorkingDirectory $projectPath

# Crear desencadenador (diario a las 2 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 2am

# Configuracion adicional
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# Crear la tarea programada
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Backup automatico diario de la base de datos Lider Pollo" `
        -User $env:USERNAME `
        -RunLevel Highest `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  TAREA CREADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalles de la tarea:" -ForegroundColor White
    Write-Host "   - Nombre: $taskName" -ForegroundColor Gray
    Write-Host "   - Frecuencia: Diaria" -ForegroundColor Gray
    Write-Host "   - Hora: 2:00 AM" -ForegroundColor Gray
    Write-Host "   - Usuario: $env:USERNAME" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para ver la tarea:" -ForegroundColor Yellow
    Write-Host "   1. Presiona Win + R" -ForegroundColor Gray
    Write-Host "   2. Escribe: taskschd.msc" -ForegroundColor Gray
    Write-Host "   3. Busca: $taskName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para probar el backup manualmente:" -ForegroundColor Yellow
    Write-Host "   Ejecuta: scripts\backup.bat" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERROR AL CREAR LA TAREA" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Asegurate de ejecutar PowerShell como Administrador" -ForegroundColor Yellow
    exit 1
}

# Pausar para que el usuario pueda leer
Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
