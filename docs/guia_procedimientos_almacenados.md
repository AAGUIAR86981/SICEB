# Guía de Procedimientos Almacenados (Stored Procedures - SPs)

Los **Procedimientos Almacenados (SP)** son bloques de código SQL que se guardan directamente dentro del servidor de base de datos. Piénsalos como "funciones" que viven en la base de datos en lugar de vivir en tu código Python.

---

## 1. ¿Qué son?
Son pequeños programas escritos en SQL (usando lógica como IF, ELSE, bucles, etc.) que se compilan una sola vez y quedan listos para ser ejecutados rápidamente por el servidor.

---

## 2. ¿Para qué se usan? (Finalidad)

1.  **Encapsulación de Lógica Compleja**: En lugar de enviar 50 líneas de código SQL desde Python, envías una sola palabra: `CALL mi_procedimiento()`.
2.  **Rendimiento**: Como ya están compilados en la base de datos, el servidor los ejecuta mucho más rápido que si enviaras el código cada vez.
3.  **Security**: Puedes darle permiso a un usuario para ejecutar un procedimiento, pero NO para ver las tablas. Esto protege los datos sensibles.
4.  **Reducción de Tráfico**: Menos datos viajando entre el servidor web y la base de datos.

---

## 3. ¿Cómo se vería un SP en lider_pollo?

Imagina que quieres simplificar el proceso de **"Generar Historial de Provisión"** que actualmente es muy largo en Python. Podrías crear un SP que lo haga todo en un solo movimiento.

### Ejemplo de creación (SQL):
```sql
DELIMITER //

CREATE PROCEDURE sp_generar_cabecera_provision(
    IN p_tipo VARCHAR(20),
    IN p_semana INT,
    IN p_nomina VARCHAR(20),
    IN p_user_id INT,
    OUT p_nuevo_id INT
)
BEGIN
    -- Lógica interna del procedimiento
    INSERT INTO provisiones_historial (tipo_provision, semana, tipo_nomina, usuario_id)
    VALUES (p_tipo, p_semana, p_nomina, p_user_id);
    
    -- Devolver el ID generado
    SET p_nuevo_id = LAST_INSERT_ID();
END //

DELIMITER ;
```

---

## 4. ¿Cómo se ejecutan? (El "Cómo")

### Desde SQL (Consola):
```sql
CALL sp_generar_cabecera_provision('semanal', 10, 'Semanales', 1, @nuevo_id);
SELECT @nuevo_id;
```

### Desde Python (Flask):
```python
cursor.callproc('sp_generar_cabecera_provision', ['semanal', 10, 'Semanales', 1, 0])
# El SP devolverá los resultados de forma eficiente
```

---

## 5. Diferencia con los TRIGGERS

| Característica | Trigger (Disparador) | Stored Procedure (SP) |
| :--- | :--- | :--- |
| **Ejecución** | Automática (al hacer un INSERT/UPDATE). | Manual (al llamarlo con `CALL`). |
| **Control** | Tú no controlas cuándo ocurre. | Tú decides exactamente cuándo lanzarlo. |
| **Uso Ideal** | Auditoría y validación de reglas. | Reportes complejos y procesos masivos. |

---

## Conclusión: ¿Por qué usarlos en lider_pollo?

La **finalidad** principal en tu proyecto sería mover la "carpintería pesada" de datos (como el guardado masivo de 1000 empleados en una provisión) a la base de datos. 

Esto haría que la página web no se quede "pensando" tanto tiempo al generar una provisión, ya que la base de datos haría todo el trabajo duro internamente.

---
> [!TIP]
> **Recomendación**: Usa Triggers para la seguridad (blindaje) y usa Stored Procedures para procesos largos que involucren muchas tablas a la vez.
