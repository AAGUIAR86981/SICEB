# Guía de Blindaje Total en SQL (Referencia Directa)

¡Excelente pregunta! La respuesta es un **SÍ** rotundo. De hecho, en el mundo de la ingeniería de datos, implementar estas reglas directamente en SQL se considera la **"Única Fuente de Verdad"**.

Aquí tienes el código consolidado para que lo apliques directamente en tu base de datos cuando estés listo.

---

## 1. Protección contra Duplicados (Fechas y Periodos)

Este código impide que se repita la misma semana y tipo de nómina en un mismo año.

```sql
-- Asegurar integridad histórica
ALTER TABLE provisiones_historial 
ADD UNIQUE INDEX idx_prevencion_fraude_periodo (semana, tipo_nomina, YEAR(fecha_creacion));
```

---

## 2. Protección de Productos y Cantidades (Regla de 4)

Este Trigger bloquea cualquier inserción que intente guardar más de 4 unidades de un producto que contenga la palabra "POLLO".

```sql
DELIMITER //
CREATE TRIGGER tr_db_blindaje_cantidades
BEFORE INSERT ON provision_productos_historial
FOR EACH ROW
BEGIN
    -- Validar cantidad máxima de 4 para productos tipo Pollo
    IF (UPPER(NEW.producto_nombre) LIKE '%POLLO%' AND NEW.cantidad > 4) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'ACCESO DENEGADO: La cantidad de Pollo no puede exceder las 4 unidades.';
    END IF;
END; //
DELIMITER ;
```

---

## 3. Normalización Automática de Nombres

Este Trigger evita que se guarden nombres en minúsculas o con espacios extra, forzando la consistencia antes de guardar.

```sql
DELIMITER //
CREATE TRIGGER tr_db_normalizar_producto
BEFORE INSERT ON catalogo_productos
FOR EACH ROW
BEGIN
    -- Convertir a Mayúsculas y quitar espacios antes y después
    SET NEW.nombre = UPPER(TRIM(NEW.nombre));
END; //
DELIMITER ;
```

---

## 4. Inmutabilidad (Evitar Modificaciones Post-Entrega)

Para que nadie pueda alterar una provisión que ya se entregó (ni siquiera por base de datos).

```sql
DELIMITER //
CREATE TRIGGER tr_db_bloqueo_historial
BEFORE UPDATE ON provision_beneficiarios
FOR EACH ROW
BEGIN
    -- Si el beneficio ya fue marcado como entregado (recibio = 1), bloquear cambios
    IF (OLD.recibio = 1) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'SEGURIDAD: No se permite modificar beneficiarios de provisiones ya procesadas.';
    END IF;
END; //
DELIMITER ;
```

---

## Ventajas de hacerlo en SQL:

1.  **Independencia del Código**: Si mañana decides cambiar tu sistema de Python a otro lenguaje, las reglas de seguridad siguen vivas en la base de datos.
2.  **Protección contra Accesos Directos**: Si alguien entra a la base de datos con un programa externo (como phpMyAdmin o DBeaver) e intenta cambiar una cantidad, la base de datos lo rechazará.
3.  **Velocidad**: Las validaciones en BD son extremadamente rápidas y no consumen recursos del servidor web.

---
> [!IMPORTANT]
> **Sobre la Verificación de Hora**: La única regla que no se puede hacer 100% en SQL es la consulta de hora a internet, ya que la base de datos usualmente no tiene acceso a sitios web externos por seguridad. Esa regla debe quedarse en el código Python o confiando en la sincronización NTP del Sistema Operativo.
