# Guía Detallada de Blindaje e Integridad (Referencia Técnica)

Este documento sirve como manual de referencia para las protecciones implementadas contra manipulación de fechas y duplicados en el sistema `lider_pollo`.

---

## 1. Restricción de Unicidad (Nivel Base de Datos) — ✅ IMPLEMENTADO

Es la garantía real de que no habrá duplicados, incluso si se altera la fecha del servidor.

### Estructura del UNIQUE Constraint

El índice único `idx_control_fraude` en la tabla `provisiones_historial` cubre:

```
UNIQUE KEY idx_control_fraude (anio_provision, tipo_nomina, tipo_provision, semana)
```

| Columna | Descripción |
|---|---|
| `anio_provision` | Columna generada (`STORED`) con el año de `fecha_creacion`. Permite reutilizar semanas entre años. |
| `tipo_nomina` | `'Semanal'` o `'Quincenal'` |
| `tipo_provision` | `'semanal'` o `'quincenal'` (slug) |
| `semana` | Número de período (ver cálculo más abajo) |

> [!IMPORTANT]
> **Corrección aplicada el 2026-02-27:** El constraint original no incluía `anio_provision`, lo que provocaba que la quincena 2 de un mes colisionara con la quincena 2 de otro mes del mismo año (error 1062). Se eliminó el constraint viejo y se recreó incluyendo `anio_provision`.

### Fórmula de Períodos

```python
# En models/provision.py → Provision.get_type_and_week()

semana_iso = serverDatetime.isocalendar()[1]   # Ej: semana 9 del año

mitad = 1 if dia_del_mes <= 15 else 2
quincena = mes * 10 + mitad                    # Ej: Feb-2ª → 22, Ene-1ª → 11
```

La codificación `MES × 10 + Q` garantiza que cada quincena sea única dentro del año:
- Enero 1ª → `11`, Enero 2ª → `12`
- Febrero 1ª → `21`, Febrero 2ª → `22`
- Diciembre 2ª → `122`

### Manejo de Errores en Python (`controllers/provision.py`)

```python
try:
    provision_id = Provision.save_history(...)
except mariadb.Error as e:
    if e.errno == 1062:  # Duplicate Entry
        flash(f"ERROR CRÍTICO: La provisión para la Semana {semProv} ({tipo_prov_slug}) ya existe en la base de datos.", "error")
    else:
        flash(f"Error de base de datos al guardar: {str(e)}", "error")
    return redirect(url_for('provision.make_provision'))
```

---

## 2. Validación de Duplicidad por Tipo (Nivel Aplicación) — ✅ IMPLEMENTADO

Antes de intentar la inserción, `Provision.exists(periodo, tipo_nomina)` verifica si ya existe una provisión de ese **tipo específico** en la **fecha de hoy**:

```python
# Semanal y Quincenal se validan de forma independiente
if Provision.exists(periodo_actual, tipo_nomina):
    flash('Error: Ya se generó esta nómina hoy.', 'error')
    return redirect(...)
```

Esto permite que en el mismo día se pueda generar tanto la nómina **Semanal** como la **Quincenal**, siempre y cuando no se hayan generado previamente.

---

## 3. Estrategia No-Retorno (Blindaje Temporal) — ✅ IMPLEMENTADO

```python
last_date = Provision.get_last_provision_date()
if last_date and datetime.now() < last_date:
    flash("BLOQUEO DE SEGURIDAD: No puede viajar al pasado.", "error")
    return redirect(...)
```

Impide generar una provisión si la fecha del servidor es menor a la de la última provisión guardada. Bloquea intentos de retroceder el reloj del sistema.

---

## 4. Verificación con Reloj de Internet — ✅ IMPLEMENTADO

Se consulta `worldtimeapi.org` para comparar la hora del servidor con la hora real de Venezuela:

```python
def check_system_time_integrity():
    api_url = "http://worldtimeapi.org/api/timezone/America/Caracas"
    response = requests.get(api_url, timeout=4)
    internet_timestamp = response.json()['unixtime']
    system_timestamp = datetime.now().timestamp()
    diff = abs(system_timestamp - internet_timestamp)
    if diff > 300:  # 5 minutos
        return False, f"Intento de manipulación detectado ({diff/60:.1f} min)"
    return True, "Sincronizado"
```

- **Tolerancia**: 5 minutos (300 segundos).
- **SSL Error**: Si hay error SSL, se bloquea (posible manipulación de fecha).
- **Sin internet**: Se permite el proceso (fallo de red genérico no es fraude).

---

## Resumen de Capas de Protección

| Nivel | Mecanismo | Qué previene | Estado |
|:---|:---|:---|:---|
| **BD (Físico)** | UNIQUE `idx_control_fraude` con `anio_provision` | Duplicados absolutos por período/año | ✅ Activo |
| **App (Pre-inserción)** | `Provision.exists()` por tipo y fecha | Doble clic / doble submit del mismo día | ✅ Activo |
| **App (Temporal)** | Estrategia No-Retorno | Retroceso manual del reloj | ✅ Activo |
| **App (API)** | Reloj de Internet | Manipulación del reloj del servidor | ✅ Activo |

---

*Última actualización: 2026-02-27 — Corrección de colisión en quincena por ausencia de año en UNIQUE constraint, y habilitación de generación independiente de ambas nóminas.*
