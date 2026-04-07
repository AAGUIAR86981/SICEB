# Manual: Implementación de Búsqueda con Sugerencias (Autocomplete)

Este manual explica cómo mejorar el buscador actual para que, mientras el usuario escribe, se muestre una lista de sugerencias con el **Nombre** y la **Cédula** del empleado, permitiendo seleccionar uno rápidamente.

---

## Opción 1: Usando `datalist` (La más sencilla y rápida)

HTML tiene una etiqueta nativa llamada `<datalist>` que crea sugerencias automáticas sin necesidad de librerías externas.

### Paso 1: Preparar la lista de sugerencias en el HTML
En el archivo `db_reports.html`, antes del input de búsqueda, añade un bloque que genere las opciones basadas en los datos que ya tienes.

```html
<!-- Lista de sugerencias (oculta por defecto) -->
<datalist id="empleadosSuggestions">
    {% for item in auditoria %}
        <option value="{{ item.nombre }} {{ item.apellido }} - {{ item.cedula }}">
    {% endfor %}
</datalist>

<!-- Tu input ahora debe estar conectado a esa lista mediante el atributo 'list' -->
<input type="text" id="searchAuditResumen" list="empleadosSuggestions" ...>
```

### Paso 2: Ajustar el JavaScript
El script que creamos en `main.js` seguirá funcionando igual, pero ahora el navegador mostrará un desplegable con las opciones que coincidan.

---

## Opción 2: Implementación Premium (Personalizada)

Si quieres que se vea mucho más profesional (con iconos y diseño personalizado), sigue estos pasos:

### Paso 1: Estructura HTML mejorada
Debemos envolver el input en un contenedor para posicionar la lista de resultados.

```html
<div class="search-wrapper" style="position: relative;">
    <input type="text" id="advancedSearch" class="form-control" placeholder="Escribir nombre o CI...">
    <div id="resultsList" class="list-group shadow" style="position: absolute; width: 100%; z-index: 1000; display: none;">
        <!-- Aquí se insertarán las sugerencias por JS -->
    </div>
</div>
```

### Paso 2: Lógica JavaScript Avanzada
Añade esta función en tu `main.js`. Esta lógica lee los datos de la tabla y crea la lista visual.

```javascript
function initAdvancedSearch(inputId, resultsId, tableId) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    const table = document.getElementById(tableId);

    input.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        results.innerHTML = '';
        
        if (val.length < 2) { // Solo buscar si hay más de 2 letras
            results.style.display = 'none';
            return;
        }

        // Obtener datos únicos de la tabla
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const matches = rows.filter(row => row.textContent.toLowerCase().includes(val));

        if (matches.length > 0) {
            results.style.display = 'block';
            matches.slice(0, 5).forEach(match => { // Mostrar máximo 5 sugerencias
                const text = match.cells[0].innerText; // Asumiendo que la celda 0 tiene el nombre
                const item = document.createElement('button');
                item.className = 'list-group-item list-group-item-action small';
                item.innerHTML = `<i class="fas fa-user-circle me-2"></i> ${text}`;
                item.onclick = () => {
                    input.value = text;
                    results.style.display = 'none';
                    // Disparar el filtrado de la tabla
                    input.dispatchEvent(new Event('keyup')); 
                };
                results.appendChild(item);
            });
        } else {
            results.style.display = 'none';
        }
    });

    // Cerrar lista si se hace clic fuera
    document.addEventListener('click', (e) => {
        if (e.target !== input) results.style.display = 'none';
    });
}
```

### Paso 3: Ventajas de este método
1. **No hay que escribir todo:** Con solo poner "123" o "Juan", el sistema te muestra las opciones completas.
2. **Experiencia de usuario (UX):** El usuario se siente guiado y evita errores de dedo.
3. **Velocidad:** Al filtrar solo los primeros 5 resultados sugeridos, la interfaz se siente muy fluida.

---

> [!TIP]
> Te recomiendo empezar con la **Opción 1 (datalist)** ya que aprovecha los datos que el servidor ya envió a la página y no requiere código complejo. Solo necesitas añadir el atributo `list` al input.
