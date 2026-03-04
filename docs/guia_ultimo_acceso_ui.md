# Guía Técnica: Registro de Último Acceso en la UI

Esta guía detalla cómo implementar un mensaje personalizado de bienvenida que muestre al usuario la fecha y hora de su conexión anterior, utilizando los datos existentes en la tabla `users`.

---

## 1. Lógica del Proceso
Para que esto funcione correctamente, debemos seguir un orden lógico:
1.  **Capturar**: Cuando el usuario hace login, primero leemos su `last_login` actual de la base de datos.
2.  **Guardar en Sesión**: Almacenamos esa "fecha vieja" en la sesión (`session['last_access']`).
3.  **Actualizar**: Ahora sí, actualizamos la base de datos con la "fecha nueva" (la de hoy).
4.  **Mostrar**: En la interfaz, leemos `session['last_access']`.

---

## 2. Cambios en el Controlador (`controllers/auth.py`)

En tu archivo, la función que maneja el inicio de sesión se llama `access`. Debes capturar el valor de la base de datos justo después de encontrar al usuario pero **antes** de actualizar su fecha de entrada.

```python
# Ubicación: controllers/auth.py -> def access()

@auth_bp.route('/auth', methods=['POST'])
def access():
    if request.method == 'POST':
        # ... (obtener username y password) ...
        try:
            user = User.get_by_username(username)
            if user:
                # 1. Capturamos el último inicio de sesión actual de la BD
                # user.original_row[8] corresponde a last_login en tu tabla
                fecha_anterior = user.original_row[8] if len(user.original_row) > 8 else None
                
                # 2. Guardamos esa fecha en la sesión (ANTES de verificar password o después)
                if pbkdf2_sha256.verify(password, user.password):
                    session['last_access'] = fecha_anterior
                    
                    # 3. El sistema luego actualiza last_login (puedes añadir el UPDATE aquí 
                    # o usar el método que ya tengas en el modelo)
                    # ... rest of your session logic ...
```

---

## 3. Cambios en la Interfaz (`templates/layout.html`)

Para mostrar el mensaje con el formato exacto que pediste:

```html
<!-- Ejemplo para colocar en la barra superior o bienvenida -->
{% if session['last_access'] %}
    <span class="badge bg-dark">
        <i class="fas fa-history me-1"></i>
        Tu última vez aquí fue el: {{ session['last_access'].strftime('%d/%m/%Y a las %H:%M') }}
    </span>
{% endif %}
```

---

## 4. Por qué en `access`?
Porque en tu proyecto es donde ocurre toda la validación de seguridad. Usar el nombre exacto de la función evita que crees código duplicado o que rompas el flujo de sesiones.

Si juntas esto con la propuesta anterior (**Registro de IP**), el mensaje podría ser aún más potente para la seguridad:

> "Tu última vez aquí fue el 25/02 desde la IP 192.168.1.10"
