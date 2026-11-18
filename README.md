# Automatización del onboarding de nuevos colaboradores

Proyecto de portafolio: automatización del proceso de onboarding de una empresa ficticia, **Austral Servicios Financieros S.A.** (~600 colaboradores, casa matriz en Santiago y 12 sucursales), con Microsoft Power Platform.

> En construcción. Este README se completa a medida que avanza el proyecto.

## Stack

- **Dataverse**: base de datos relacional (8 tablas dentro de una solución)
- **Power Apps**: app de lienzo para que Personas registre ingresos y siga su avance, y app basada en modelo para administrar las tablas
- **Power Automate**: creación de tareas, avisos y recordatorios por atraso
- **Power BI**: dashboard de cumplimiento y experiencia de onboarding
- **Copilot Studio**: agente que responde las preguntas de los nuevos colaboradores
- **Python (pandas)**: generación y validación del histórico sintético

## El proceso

Cuando Personas registra un ingreso, se crean automáticamente 14 tareas para TI, Administración, Personas, la jefatura, el tutor y el propio colaborador, cada una con su fecha de compromiso (fecha de ingreso + día relativo). El proceso va desde 10 días antes del ingreso hasta la evaluación del período de prueba (día 85).

## Modelo de datos

```
Área ──< Cargo ──< Ingreso >── Sucursal
                     │
                     ├──< Tarea de onboarding >── Plantilla de tarea
                     │
                     └──< Encuesta de onboarding

Responsable (tabla independiente: a quién avisar por rol)
```

Todo vive en la solución **Onboarding Austral** (prefijo `aus`). El detalle de tablas, columnas y decisiones de diseño está en [`dataverse/tablas.md`](dataverse/tablas.md).

## La app

App de lienzo para el equipo de Personas, con tres pantallas:

| Pantalla | Qué hace |
|---|---|
| **Inicio** | Lista de ingresos con buscador y filtro por estado, ordenada por fecha de ingreso |
| **Nuevo ingreso** | Formulario que genera el ID automáticamente, muestra la sucursal solo para cargos de sucursal, sugiere la jefatura según el cargo o la sucursal y advierte cuando quedan menos de 5 días para el ingreso |
| **Detalle** | Datos del ingreso, barra de avance y lista de tareas con colores por situación (a tiempo, con atraso, atrasada, pendiente); permite marcar tareas como completadas. Al completar la tarea *Asignar tutor* (T06), la jefatura debe indicar el tutor: queda guardado en el ingreso y asignado a la tarea *Inducción del cargo* (T10) |

La app solo registra ingresos y actualiza tareas: la creación de las tareas y los cambios de estado del ingreso los hacen los flujos de Power Automate, para que la lógica de negocio viva en un solo lugar.

El tutor no se pide al registrar el ingreso: según el proceso lo define la jefatura en la tarea T06, así que se registra ahí.

Además, una **app basada en modelo** (*Administración Onboarding*) permite ver y editar todas las tablas.

## La automatización

| Flujo | Se activa | Qué hace | Estado |
|---|---|---|---|
| **Crear tareas del ingreso** | Cuando se crea un ingreso | Recorre la plantilla y crea las 14 tareas que aplican a la sede del ingreso, con su fecha de compromiso (fecha de ingreso + día relativo) y su responsable | Listo |
| **Revisión diaria** | Todos los días | Pasa los ingresos a *En curso* cuando llega su fecha y envía recordatorios de tareas atrasadas | Pendiente |
| **Cierre del ingreso** | Cuando se completa una tarea | Marca el ingreso como *Completado* cuando ya no le quedan tareas pendientes | Pendiente |

Cómo funciona el flujo de creación de tareas:

1. **Desencadenador:** fila creada en *Ingresos*.
2. **Obtener una fila por id:** lee el ingreso completo, que incluye las etiquetas de las opciones.
3. **Sede:** guarda la etiqueta de la sede (*Casa matriz* o *Sucursal*).
4. **Enumerar filas:** trae la plantilla de tareas.
5. **Por cada tarea de la plantilla:** si aplica a *Todos* o a la sede del ingreso, determina a quién se asigna (jefatura, tutor, el propio colaborador o la persona definida en *Responsables* para TI, Personas y Administración) y crea la tarea con sus búsquedas al ingreso y a la plantilla.

Las tareas nuevas usan un ID legible que combina el ingreso y el código de la tarea (`ING-0175-T04`).

## Los datos

El histórico es sintético y se genera con Python: **173 ingresos, 2.352 tareas y 136 encuestas** entre mayo 2025 y octubre 2026. Como los datos son sintéticos, se simularon tres problemas operacionales realistas que el dashboard debe hacer visibles:

1. TI se atrasa bastante más en los meses de peak de contratación (marzo y agosto).
2. Las sucursales regionales tienen más atrasos en la entrega de equipo y puesto.
3. Los ingresos registrados con menos de 5 días de anticipación concentran los atrasos y tienen peor satisfacción.

El script genera dos versiones de los mismos datos:

| Carpeta | Encabezados | Uso |
|---|---|---|
| `datos/csv/` | Técnicos (`FechaIngreso`) | Análisis con Python o Power BI |
| `datos/csv_dataverse/` | Iguales a las columnas de Dataverse ("Fecha de ingreso"), numerados en orden de importación | Importación a Dataverse |

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `docs/` | Documento de diseño y capturas |
| `datos/` | Script generador del histórico y CSV resultantes |
| `dataverse/` | Modelo de datos, relaciones y orden de importación |
| `power-platform/` | Solución exportada (tablas, apps, flujos y agente) |
| `power-bi/` | Archivo del dashboard |
| `copilot-studio/` | Base de conocimiento del agente |

## Avance

- [x] Paso 1: diseño del proceso y modelo de datos
- [x] Paso 2: histórico sintético (173 ingresos, 2.352 tareas, mayo 2025 a octubre 2026)
- [x] Paso 3: tablas en Dataverse e importación de datos
- [x] Paso 4: app de lienzo para registrar ingresos y seguir su avance
- [ ] Paso 5: flujos de Power Automate (creación de tareas lista; revisión diaria y cierre pendientes)
- [ ] Paso 6: dashboard en Power BI
- [ ] Paso 7: agente en Copilot Studio
- [ ] Paso 8: video demo

## Desafíos y aprendizajes

- **De SharePoint a Dataverse.** El diseño original usaba listas de SharePoint, pero el tenant de desarrollo no incluye SharePoint. Se migró el modelo a Dataverse, lo que permitió usar relaciones reales (columnas de búsqueda) en vez de claves de texto.
- **Validación de datos en el origen.** Al revisar reglas de negocio sobre el histórico se detectó que 47 de 173 registros caían en fin de semana. Se corrigió en el generador (el registro pasa al viernes anterior) y se agregaron validaciones: ningún registro posterior al ingreso ni a la fecha de corte, y días de anticipación coherentes con las fechas.
- **Fechas y zona horaria.** Las columnas de fecha usan el comportamiento *Solo fecha*; con el valor por defecto (*Usuario local*) Dataverse guarda en UTC y en Chile las fechas pueden aparecer un día antes.
- **Dos importadores, dos comportamientos.** El importador moderno de Excel/CSV cargó bien las tablas sin búsquedas, pero en las tablas con búsquedas fallaba sin mostrar errores. La causa: cada tabla tiene un identificador único con el mismo nombre para mostrar que la tabla (por ejemplo, dos columnas "Cargo"). Se resolvió con el importador clásico desde la app basada en modelo, que permite elegir el destino de cada columna, resuelve las búsquedas por la columna principal y deja un registro de errores por fila.
- **Delegación en Power Apps.** La tabla de tareas tiene más de 2.000 filas, el máximo que Power Apps procesa localmente. El filtro de tareas de un ingreso compara el identificador único de la búsqueda, una operación delegable que resuelve Dataverse en el servidor; con un filtro no delegable, los ingresos más recientes habrían aparecido sin tareas y sin ningún error.
- **Datos relacionados en cuadros combinados.** El cuadro combinado de Cargo no traía los datos del Área relacionada, por lo que la jefatura sugerida quedaba vacía en casa matriz. Se resolvió con `LookUp` directo a la tabla de cargos, que trae el registro completo con sus relaciones.
- **Errores en cascada.** Un error en la propiedad *Items* de una galería hace que fallen todas sus etiquetas, porque `ThisItem` pierde sus columnas: la causa estaba en la galería, no en las etiquetas.
- **Conflictos de nombres entre tablas y columnas.** Con el plural de una tabla igual a su singular, Power Apps interpretaba la columna de búsqueda *Ingreso* como la tabla completa. Se resolvió con `ThisRecord` y corrigiendo los plurales de las tablas.
- **El desencadenador de Dataverse no trae las etiquetas de las opciones.** Solo envía el número interno (`751830001`), por lo que la comparación con la etiqueta *Sucursal* fallaba y no se creaba la tarea de equipo para sucursales. Se resolvió leyendo la fila completa con *Obtener una fila por id*, que sí incluye las etiquetas, sin dejar números escritos a mano en el flujo.
- **Depurar una condición con "Ver código".** El diseñador solo muestra el resultado de una condición, no los valores comparados. Al revisar su código se vio que comparaba contra la sede del desencadenador (el número) en vez de la salida del paso *Sede*: dos campos casi iguales en el contenido dinámico.
- **Búsquedas en Power Automate.** Una columna de búsqueda no se llena con el texto visible sino con la referencia `conjunto(GUID)`, por ejemplo `aus_plantilladetareas(...)`. El nombre del conjunto de entidades se puede confirmar en las salidas sin procesar de un paso (`@odata.context`).
- **Autenticación de conexiones.** La conexión de Dataverse fallaba al crearse desde el diseñador de flujos porque el navegador bloqueaba las cookies de terceros que necesita la ventana de inicio de sesión de Microsoft. Se resolvió permitiéndolas, y la conexión se maneja con una *referencia de conexión* dentro de la solución, para que el flujo se pueda importar en otro entorno sin modificarlo.
- **El formulario debe seguir al proceso.** Al probar el sistema se detectó que el registro exigía el tutor, un dato que según el proceso todavía no existe en ese momento (lo define la jefatura en la tarea T06). Se sacó del formulario y se pide al completar la T06.
- **Nombres que chocan con columnas de sistema.** Toda tabla trae columnas *Estado* y *Razón para el estado*, por eso las columnas propias se llaman *Estado ingreso* y *Estado tarea*.

## Cómo regenerar los datos

```bash
python -m pip install -r requirements.txt
python datos/generar_historico.py
```

Usa una semilla fija, por lo que siempre genera los mismos datos. Al final imprime un resumen que permite verificar que los patrones quedaron en los datos.
