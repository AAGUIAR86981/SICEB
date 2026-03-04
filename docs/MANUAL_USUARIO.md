# Manual de Usuario - SICEB (Sistema de Control de Entregas de Provisiones)

## Introducción
Bienvenido al manual de usuario del sistema SICEB. Este documento le guiará a través de todas las funcionalidades del sistema diseñado para gestionar la entrega de provisiones a los empleados de la empresa Lider Pollo.

---

## 1. Acceso al Sistema

### Inicio de Sesión
1.  Abra su navegador web e ingrese a la dirección del sistema.
2.  En la pantalla de bienvenida, ingrese su **Usuario** y **Contraseña**.
3.  Haga clic en **"Entrar"**.

> **Nota:** Si olvida su contraseña, deberá contactar al Administrador del sistema para restablecerla.

### Roles de Usuario
El sistema maneja diferentes niveles de acceso:
- **Administrador**: Acceso total a todas las funciones (Usuarios, Configuración, Catálogos, Provisiones, Reportes).
- **Supervisor**: Gestión de empleados, combos y realización de provisiones.
- **Usuario Estándar**: Consultas básicas.
- **Visualizador**: Solo lectura de reportes.

---

## 2. Pantalla Principal (Dashboard)
Una vez dentro, verá el menú principal con las siguientes opciones (según sus permisos):
- **Gestión de Empleados**: Altas, bajas y modificaciones.
- **Catálogos**: Configuración de departamentos, productos y combos.
- **Provisiones**: Configurar y realizar la entrega de provisiones.
- **Historial**: Consultar entregas pasadas.
- **Consultas**: Búsqueda detallada de beneficios por empleado.

---

## 3. Gestión de Empleados

### Registrar Nuevo Empleado
1.  Vaya a **"Gestión de Empleados"** > **"Registrar Empleado"**.
2.  Complete el formulario con:
    - Cédula
    - Nombre y Apellido
    - Departamento (Seleccione de la lista)
    - Tipo de Nómina (Semanal/Quincenal)
    - ID Empleado (Número de reloj/ficha)
    - Fecha de Ingreso
3.  Haga clic en **"Guardar"**.

### Importar Empleados (Masivo)
> **Nota Importante**: La información de los empleados debe provenir de la base de datos **BioStar**. Asegúrese de generar el reporte desde dicho sistema antes de importarlo aquí.

1.  En la misma sección, busque la opción **"Cargar Excel"**.
2.  Seleccione un archivo `.xlsx` exportado de BioStar (o con el formato compatible) que contenga las columnas requeridas.
3.  El sistema procesará el archivo y notificará cuántos registros se cargaron correctamente.

### Editar/Desactivar Empleado
- Utilice el buscador para encontrar al empleado por nombre o cédula.
- **Editar**: Modifique los datos y guarde.
- **Desactivar**: Cambie el estado a "Inactivo" para que no aparezca en las provisiones, sin eliminar su historial.

---

## 4. Gestión de Catálogos

### Departamentos y Tipos de Nómina
- Desde el menú **"Catálogos"**, puede agregar nuevos departamentos o tipos de nómina.
- **Importante**: Evite eliminar departamentos que tengan empleados activos asignados.

### Productos y Combos
1.  **Productos**: Registre los ítems individuales (ej. "Pollo Entero", "Cartón de Huevos").
2.  **Combos**: Agrupe productos para facilitar la entrega.
    - Cree un combo (ej. "Combo Semanal A").
    - Asigne los productos y cantidades que lo componen.
    - Active el combo para que aparezca disponible al realizar provisiones.

---

## 5. Proceso de Provisión

### Configurar Provisión
*(Solo Administradores/Supervisores)*
Antes de entregar, asegúrese de que la semana o quincena esté activa. El sistema calcula automáticamente el número de semana basado en la fecha actual.

### Realizar Provisión
1.  Vaya a **"Realizar Provisión"**.
2.  El sistema detectará automáticamente si es **Semana** o **Quincena**.
3.  Seleccione el **Combo** a entregar.
4.  Verá una lista de todos los empleados activos para esa nómina (Pre-Asignados).
5.  **Excepciones**: Si algún empleado NO debe recibir provisión esta vez, búsquelo en la lista y desmárquelo o muévalo a la lista de "No Recibe".
6.  Haga clic en **"Procesar Provisión"**.

> **Confirmación**: El sistema guardará el registro y generará un ID de provisión único.

---

## 6. Reportes e Historial

### Historial de Provisiones
- Consulte todas las entregas realizadas filtrando por fecha o tipo.
- Haga clic en **"Ver Detalles"** para ver qué empleados recibieron en una fecha específica.

### Consultar Beneficios por Empleado
- Vaya a **"Consultas"**.
- Ingrese la cédula de un empleado.
- El sistema mostrará todas las fechas en que recibió provisión y qué combo se le entregó.

### Exportar Datos
En casi todas las pantallas de reportes, encontrará botones para:
- **Exportar a Excel**: Para análisis detallado.
- **Exportar a PDF**: Para impresión y archivo físico.

---

## 7. Panel de Administración
*(Exclusivo Administradores)*
- **Usuarios del Sistema**: Cree cuentas para otros operadores y asigne roles.
- **Auditoría**: Revise el registro de actividades para ver quién realizó cambios en el sistema (logs de seguridad).

---

## 8. Integración Futura (Biometría)
El sistema SICEB está preparado para integrarse con dispositivos de control de asistencia biométricos en el futuro.

### Funcionalidad Prevista
Una vez implementado, el sistema podrá:
1.  **Validación Automática**: Cruzar la información de asistencia (huella/rostro) con las reglas de negocio.
2.  **Suspensión de Beneficios**: Desactivar automáticamente la provisión para empleados que no cumplan con el mínimo de asistencia o condiciones requeridas en la semana.
3.  **Reportes de Asistencia**: Visualizar junto con la entrega de provisiones los días trabajados por cada colaborador.

Esta característica requerirá la instalación de dispositivos compatibles y la configuración de un módulo de conexión adicional.

---

## Soporte
Para problemas técnicos o dudas no cubiertas en este manual, contacte al departamento de sistemas.
