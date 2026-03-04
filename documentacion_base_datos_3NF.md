# Documentación del Modelo de Base de Datos y Normalización (3NF)

Esta documentación explica el diseño de la base de datos del proyecto SICEB (Líder Pollo), enfocándose en por qué ciertas tablas no cumplen de manera estricta con la Tercera Forma Normal (3NF) y las razones técnicas por las que es una buena práctica mantenerlo así en determinados módulos de este sistema.

## ¿Qué es la Tercera Forma Normal (3NF)?
En el diseño de bases de datos, la 3NF es una regla de normalización que decreta que una tabla no debe contener datos redundantes. Específicamente, establece que **todo campo no clave debe depender única y exclusivamente de la clave principal (ID)**. 

Por ejemplo, si guardas el `empleado_id`, en esa misma tabla no deberías guardar el `nombre` del empleado ni su `departamento`, porque esos datos ya existen en la tabla central de `empleados` y se pueden consultar fácilmente relacionando las tablas (`JOIN`).

## Desnormalización Intencional en el Sistema Líder Pollo
En este sistema, existen varias tablas fundamentales enfocadas a historial y auditoría que rompen la regla de la 3NF de manera *intencional*:

### 1. Tablas Afectadas
* **`provisiones_historial`**: Almacena el `usuario_id` del creador, pero también guarda textualmente el `usuario_nombre`. Además guarda el tipo de nómina.
* **`provision_beneficiarios`**: Guarda el `empleado_id` (vinculación real a la tabla base), pero paralelamente almacena la `cedula`, `nombre_completo` y `departamento` del empleado tal y como estaban en ese instante.
* **`user_activities`**: Guarda el `user_id` de la persona que realizó la acción y redundantemente almacena el `username`.

### 2. ¿Por qué se diseñó de esta forma? (Justificación Técnica)
La desnormalización en tablas de tipo "Historial", "Log" o "Ticket/Factura" no es un error, sino que representa una técnica vital conocida como "Data Snapshotting" (Captura de datos inmutables) por tres razones determinantes:

1. **Inmutabilidad del Historial (Snapshot o "Foto en el tiempo"):** 
   Si en la Semana 10 del año hacemos una provisión para el empleado "Juan Pérez" que en ese entonces trabajaba en "Ventas", la provisión **DEBE** registrar textualmente esa realidad. 
   Si la base de datos estuviera 100% en 3NF y solo guardara su `empleado_id`, el día en que muevan a Juan Pérez al departamento "Marketing", todas las consultas a provisiones antiguas dictarán erróneamente que las recibió estando en "Marketing". Esto destruiría los reportes contables históricos, ya que alteraríamos el pasado basándonos en el presente. Al almacenar copias en texto (nombre, departamento), "congelamos" el tiempo y garantizamos reportes 100% fieles a la fecha del evento.

2. **Beneficios de Rendimiento (Performance):** 
   Tablas de logs e historiales están destinadas a crecer enormemente en cantidad de registros. Leer datos de una tabla de `user_activities` que ya contenga el "username" textualmente pre-volcado es extremadamente eficiente y rápido. Si cada reporte tuviese que cruzar repetidamente relaciones mediante `JOIN` a las tablas base (`users`, `empleados`, `departamentos`), los reportes tardarían mucho más en generarse sin mayor beneficio práctico.

3. **Prevención de Registros "Huérfanos" (Eliminaciones en base):** 
   Si se elimina intencionalmente o por error a un usuario del sistema o de un catálogo, los historiales pasados sobrevivirán. Seguiremos sabiendo quién realizó la acción, cómo se llamaba y en qué área operaba al momento del hecho, ya que sus datos trascendentales están asegurados repetidamente.

## Solución Aplicada Recientemente (Protección con Llaves Foráneas)
Para mantener esta flexibilidad de registro histórico, pero al mismo tiempo blindar y organizar profesionalmente la Base de Datos, se aplicó una técnica de **Integridad Referencial**:

* Se añadieron o corroboraron las **Foreign Keys (Llaves Foráneas)** con la regla lógica `ON DELETE SET NULL` en tablas como `user_activities` (`user_id` vinculado al id de la tabla `users`) y de igual forma en `provisiones_historial`.
* **Esto garantiza que:** La base de datos no permitirá jamás la creación de un nuevo registro histórico asigando a un ID inventado o inexistente. Esto provee fiabilidad estricta y evita "basura digital", permaneciendo de fondo e invisible a tu aplicación en Python actual, por lo que nada se rompe ni se altera en el funcionamiento ordinario.

**Conclusión final:** En sistemas serios de nivel empresarial que resguardan trazabilidades, finanzas o auditorías, aplicar los estándares más estrictos 3NF de manera generalizada arruina la fidelidad forense de los hechos. El modelo de arquitectura híbrido con llaves referenciales como en el actual proyecto Líder Pollo, es un enfoque probado, seguro y altamente recomendando para equilibrar rendimiento e historia digital.


