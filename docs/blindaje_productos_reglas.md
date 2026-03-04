# Blindaje de Productos y Reglas de Negocio

Este documento detalla cómo implementar restricciones de integridad para el catálogo de productos y reglas de negocio específicas para la entrega de provisiones, sin modificar el código actual.

---

## 1. Normalización de Nombres (Evitar "pollos" vs "Pollos")

Actualmente, si la base de datos usa una colación binaria (como `utf8mb4_bin`), permite nombres duplicados que solo varían en mayúsculas. Para evitar esto:

### Solución A: Cambio de Colación (Recomendado)
Cambiar la colación de la columna a una que sea "Case Insensitive" (CI).
```sql
ALTER TABLE catalogo_productos 
MODIFY nombre VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci UNIQUE;
```

### Solución B: Trigger de Normalización (Sin cambiar estructura)
Un disparador que convierta todo a mayúsculas antes de insertar o actualizar.
```sql
DELIMITER //
CREATE TRIGGER tr_productos_nombre_upper
BEFORE INSERT ON catalogo_productos
FOR EACH ROW
BEGIN
    SET NEW.nombre = UPPER(TRIM(NEW.nombre));
END; //
DELIMITER ;
```

---

## 2. Límite de Cantidad (Regla de los "4 Pollos")

Para asegurar que no se entreguen más de 4 unidades de un producto específico (ej. Pollo) por empleado, se pueden usar dos capas:

### Nivel Aplicación (Python)
En el modelo que gestiona la creación de combos o la asignación de provisiones:

```python
def validar_regla_pollo(productos_list):
    MAX_POLLO = 4
    for nombre, cantidad in productos_list:
        if "POLLO" in nombre.upper():
            if int(cantidad) > MAX_POLLO:
                raise ValueError(f"Alerta: No se permiten más de {MAX_POLLO} pollos por empleado.")
```

### Nivel Base de Datos (Seguridad Máxima)
Un `CHECK CONSTRAINT` (MariaDB 10.2+) o un Trigger que valide la cantidad.

```sql
-- Detener la inserción en el historial si la cantidad de pollo excede 4
DELIMITER //
CREATE TRIGGER tr_validar_cantidad_pollo
BEFORE INSERT ON provision_productos_historial
FOR EACH ROW
BEGIN
    IF (NEW.producto_nombre LIKE '%POLLO%' AND NEW.cantidad > 4) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Cantidad de pollo excede el límite permitido de 4 por empleado.';
    END IF;
END; //
DELIMITER ;
```

---

## 3. Protección contra Modificaciones No Autorizadas

Para evitar que alguien cambie las cantidades de un producto una vez que ya está definido en un combo o en el historial.

### Auditoría de Cambios
Usar una tabla de logs (similar a `user_activities`) disparada por cambios en productos.

```sql
CREATE TABLE audit_productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    valor_anterior INT,
    valor_nuevo INT,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger para detectar cambios en catalogo_productos
CREATE TRIGGER tr_audit_product_update
AFTER UPDATE ON catalogo_productos
FOR EACH ROW
    INSERT INTO audit_productos(producto_id, valor_anterior, valor_nuevo)
    VALUES (OLD.id, OLD.precio_o_cantidad, NEW.precio_o_cantidad);
```

### Bloqueo de Historial (Inmutabilidad)
Evitar cualquier `UPDATE` en la tabla de historial de provisiones.

```sql
CREATE TRIGGER tr_bloquear_edicion_historial
BEFORE UPDATE ON provision_productos_historial
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'Los registros de provisiones ya procesadas no pueden ser modificados.';
END;
```

---

## Resumen de Aplicación

| Desafío | Herramienta | Resultado |
| :--- | :--- | :--- |
| **Duplicados por nombres** | Colación CI o Trigger UPPER | "Pollo", "pollo" y "POLLO" serán tratados como el mismo registro. |
| **Límite de 4 unidades** | Trigger en `provision_productos` | El sistema rechazará físicamente cualquier intento de entregar 5 pollos. |
| **Cambios no autorizados** | Triggers de Auditoría/Bloqueo | Se registra quién cambió qué, o se impide la edición de facturas pasadas. |

---
> [!TIP]
> **Dato Clave**: Implementar estas reglas en la **Base de Datos** es mucho más seguro que hacerlo solo en Python, ya que protege la información incluso si alguien intenta entrar directamente a la base de datos sin usar el sistema web.
