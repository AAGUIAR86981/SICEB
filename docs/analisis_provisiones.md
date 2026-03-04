# Análisis del Proceso "Generar Provisiones" - SICEB

Este documento detalla el funcionamiento técnico del proceso de generación de provisiones en el proyecto `lider_pollo`, basándose en el análisis de los controladores, modelos y la estructura de la base de datos.

## 1. Preparación del Formulario (`make_provision` — GET)

Cuando el usuario accede a la pantalla de "Realizar Provisión":

- **Cálculo de Períodos**: El sistema calcula de forma automática **ambos** períodos del día actual (semanal y quincenal), sin forzar ningún tipo. Los valores se calculan en `Provision.get_type_and_week()`.
- **Verificación de Estado**: Se consulta la BD para determinar si cada tipo de nómina ya fue generado **hoy**. Esta información se pasa al template para mostrar el estado visual de cada opción.
- **Carga de Combos**: Se consultan los combos activos desde la tabla `combos`, incluyendo el detalle de sus productos (`combo_items` + `catalogo_productos`).
- **Variables de Template**: Se pasan al template `realizarP.html`: `semana_iso`, `quincena`, `semanal_ya_hecha`, `quincenal_ya_hecha`.

## 2. Fórmula de Períodos (`Provision.get_type_and_week`)

| Tipo      | Cálculo                              | Ejemplo (27-Feb-2026)      |
|-----------|--------------------------------------|----------------------------|
| Semanal   | `semana_iso` = número de semana ISO (1–53) del año | `9`         |
| Quincenal | `quincena` = `MES × 10 + Q` donde Q=1 si día ≤ 15, Q=2 si día > 15 | `22` (feb 2ª quincena) |

> [!NOTE]
> El formato `MES × 10 + Q` para la quincena garantiza unicidad dentro del mismo año:
> - Enero 1ª quincena → `11`, Enero 2ª quincena → `12`
> - Febrero 1ª quincena → `21`, Febrero 2ª quincena → `22`
> - Diciembre 2ª quincena → `122`

## 3. Procesamiento y Lógica de Negocio (`procesar_provision_post`)

Al enviar el formulario, el sistema ejecuta las siguientes validaciones en orden:

### A. Validación de Nómina Seleccionada
Se verifica que el campo `Nomina` (valor `1`=Semanal o `2`=Quincenal) esté presente.

### B. Validación de Duplicidad (por tipo, independiente)
El sistema consulta `provisiones_historial` para verificar si ya existe una provisión del **mismo tipo de nómina** en la fecha actual (`CURDATE()`). **Semanal y Quincenal son independientes**: se puede generar una aunque la otra ya exista.

### C. Estrategia No-Retorno (Blindaje temporal)
Se verifica que la fecha actual no sea anterior a la última provisión registrada. Impide retroceder en el tiempo.

### D. Verificación de Reloj de Internet
Se consulta `worldtimeapi.org` para comparar la hora del servidor con la hora de internet. Si el desfase supera 5 minutos, el proceso se bloquea como medida antifraude.

### E. Segmentación de Beneficiarios
El sistema consulta la tabla `empleados`:
1. **Asignados**: Empleados activos (`boolValidacion = 1`) del tipo de nómina seleccionado.
2. **Invalidados**: Empleados inactivos (`boolValidacion = 0`) que no recibirán el beneficio.

### F. Mapeo de Productos
Se recuperan nombres y cantidades del combo seleccionado.

## 4. Persistencia en Base de Datos (`Provision.save_history`)

Se realiza dentro de una **transacción** para garantizar atomicidad:

1. **Cabecera (`provisiones_historial`)**: Registro principal con metadatos, usuario, resumen estadístico en JSON y la IP del solicitante.
2. **Detalle de Productos (`provision_productos_historial`)**: Desglose del combo por producto.
3. **Asignación Individual (`provision_beneficiarios`)**: Un registro por empleado (asignado o invalidado) para trazabilidad histórica.

## 5. Interfaz de Usuario (`realizarP.html`)

- **Selección de Nómina**: Dos radio buttons (`Semanal` / `Quincenal`), cada uno muestra su período correspondiente entre paréntesis.
- **Estado Visual**: Si una nómina ya fue generada hoy, aparece un badge verde ✓ y el radio queda **deshabilitado**.
- **Período Dinámico**: Al seleccionar una nómina, el panel izquierdo muestra en tiempo real el período correspondiente (ej: "Semana Nº 9" o "2ª quincena de Febrero").
- **Ambas generadas**: Si ambas nóminas ya fueron procesadas hoy, aparece un mensaje informativo en el formulario.

## 6. Visualización de Resultados

Los datos se cargan en la sesión de Flask y se muestran en `resultados_provision.html`, con opción de exportar en Excel o CSV segmentados por "Asignados" o "Invalidados".

---

> [!NOTE]
> El sistema utiliza un esquema híbrido: guarda datos relacionales (para reportes rápidos) y datos en formato JSON (para auditoría inmutable), garantizando que la información histórica no se pierda si se eliminan productos o departamentos en el futuro.

---

*Última actualización: 2026-02-27 — Ajuste para generación independiente de ambas nóminas y corrección del cálculo de quincena.*
