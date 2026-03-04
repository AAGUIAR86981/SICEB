> [!NOTE]
> **ESTADO: RESUELTO Y ELIMINADO (Marzo 2026)**
> 
> Tras el análisis a continuación, se procedió a **eliminar permanentemente** la tabla `provision_configs` de la base de datos (MaríaDB), así como cualquier ruta (`/configurar_provision`), referencias en `manage_db.py`, `init_database.py` y plantillas. El código fuente y la base de datos ahora están limpios de esta funcionalidad legada. El documento a continuación se mantiene exclusivamente como bitácora histórica de la decisión.
> 
> ---

# Análisis de Funcionalidad: ¿Se usan `provision_configs` y `configurar_provision`?


Tras una revisión exhaustiva del código fuente y la base de datos del proyecto `lider_pollo`, aquí tienes la respuesta técnica definitiva: **Tienes razón, actualmente son funcionalidades redundantes (no se usan para el proceso principal).**

---

## 🔍 Hallazgos Técnicos

1.  **Ruta Huérfana**: La ruta `/configurar_provision` y su plantilla HTML existen, pero **no hay ningún botón ni enlace** en todo el sistema (ni en el menú, ni en el panel de administrador) que lleve a ellas.
2.  **Cálculo en Tiempo Real**: El sistema ya no necesita que configures la semana manualmente. El archivo `models/provision.py` tiene una función llamada `get_type_and_week()` que calcula automáticamente:
    *   La **Semana ISO** (1-52) basándose en la fecha del servidor.
    *   La **Quincena** (1 o 2) basándose en si hoy es antes o después del día 15.
3.  **Independencia del Historial**: La tabla `provisiones_historial` (donde se guarda el éxito de la provisión) **no depende** de la tabla de configuraciones. Guarda la semana y el tipo de nómina directamente como texto.

---

## ❓ ¿Por qué siguen ahí?

Parecen ser **restos de una versión anterior** del sistema donde quizás el administrador debía "abrir" la semana manualmente antes de que los supervisores pudieran trabajar. Actualmente:
*   Si la tabla `provision_configs` está vacía, el sistema muestra un mensaje de "Error: No se encontraron configuraciones", pero **te permite seguir adelante igualmente** usando los valores automáticos.
*   El campo `provision_config_id` se guarda en la sesión pero **nadie lo usa** para el guardado final en la base de datos.

---

## 💡 Recomendación

Si quieres limpiar el proyecto y evitar confusiones a futuro:

1.  **No es necesario borrarlos ahora**: No afectan el rendimiento ni causan errores.
2.  **Se pueden ignorar**: Puedes tratarlos como "código legado" (legacy code).
3.  **Fase de Limpieza**: En una futura actualización, podrías eliminar esa ruta y la tabla para simplificar la base de datos.

---
> [!NOTE]
> **Conclusión**: Tu instinto fue correcto. El proceso de generar provisiones es ahora más automático y ya no depende de esa configuración manual previa.
