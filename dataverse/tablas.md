# Modelo de datos en Dataverse

Todo vive dentro de una **solución** de Power Platform:

- **Solución:** Onboarding Austral
- **Editor (publisher):** Austral, prefijo `aus` → las tablas y columnas quedan como `aus_ingreso`, `aus_fechaingreso`, etc.

La app, los flujos y el agente se crean dentro de esta misma solución, así todo el proyecto se exporta como un solo `.zip` a `power-platform/`.

## Diagrama de relaciones

```
Área ──< Cargo ──< Ingreso >── Sucursal
                     │
                     ├──< Tarea de onboarding >── Plantilla de tarea
                     │
                     └──< Encuesta de onboarding

Responsable (tabla independiente: a quién avisar por rol)
```

`A ──< B` = una fila de A tiene muchas de B (B tiene una columna de búsqueda hacia A).

## Decisiones de diseño

- **Relaciones reales con columnas de búsqueda (lookup).** Dataverse es una base relacional: la Tarea apunta a su Ingreso y a su Plantilla, el Ingreso a su Cargo y Sucursal. Power Apps, Power BI y Copilot Studio entienden estas relaciones sin configuración extra.
- **El Área no se guarda en el Ingreso:** se obtiene a través del Cargo (normalización). La Sede sí se guarda, porque el flujo la usa para elegir las tareas (T03 o T04).
- **La Tarea guarda una copia del nombre, fase y responsable** aunque tenga búsqueda a la Plantilla. Si mañana cambia la plantilla, el histórico no se altera.
- **Fechas con comportamiento "Solo fecha".** Si se dejan como "Usuario local", Dataverse las guarda en UTC y en Chile pueden aparecer corridas un día.
- **Sí/No como opción (Choice) y no como columna Sí/No.** Los CSV traen "Sí"/"No" en español y así la importación los reconoce sin problemas de idioma.
- **Personas como texto + correo.** Jefaturas, tutores y colaboradores son ficticios y no existen en el tenant. Para la demo, los correos de **Responsable** se cambian por cuentas reales para que los avisos lleguen.

## Orden de importación

Las tablas referenciadas van primero, para que las búsquedas encuentren a qué apuntar:

1. Área
2. Sucursal
3. Responsable
4. Plantilla de tarea
5. Cargo (busca Área)
6. Ingreso (busca Cargo y Sucursal)
7. Tarea de onboarding (busca Ingreso y Plantilla de tarea)
8. Encuesta de onboarding (busca Ingreso)

Las búsquedas se resuelven por la **columna principal** de la tabla de destino. Por eso cada columna principal es el nombre o código que aparece en los CSV.

## Tablas

La columna marcada como **Principal** es la columna de nombre de la tabla (la que se renombra al crearla).

### Área — `Areas.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| Área | **Principal** (texto) | Area |
| Jefatura | Texto | Jefatura |
| Correo jefatura | Correo electrónico | CorreoJefatura |

### Sucursal — `Sucursales.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| Sucursal | **Principal** (texto) | Sucursal |
| Región | Texto | Region |
| Regional | Opción: Sí, No | Regional |
| Jefatura | Texto | Jefatura |
| Correo jefatura | Correo electrónico | CorreoJefatura |

### Responsable — `Responsables.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| Rol | **Principal** (texto) | Rol |
| Persona asignada | Texto | PersonaAsignada |
| Correo | Correo electrónico | Correo |

### Plantilla de tarea — `PlantillaTareas.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| Código | **Principal** (texto) | Codigo |
| Tarea | Texto | Tarea |
| Responsable | Opción: Personas, TI, Administración, Jefatura, Tutor, Colaborador | Responsable |
| Día relativo | Número entero | DiaRelativo |
| Fase | Opción: Pre-ingreso, Primer día, Primera semana, Primer mes, Cierre | Fase |
| Aplica a | Opción: Todos, Casa matriz, Sucursal | AplicaA |
| Activa | Opción: Sí, No | Activa |

### Cargo — `Cargos.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| Cargo | **Principal** (texto) | Cargo |
| Área | Búsqueda → Área | Area |
| Sede | Opción: Casa matriz, Sucursal | Sede |

### Ingreso — `Ingresos.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| ID ingreso | **Principal** (texto) | IngresoID |
| Nombre colaborador | Texto | Nombre |
| Correo personal | Correo electrónico | CorreoPersonal |
| Cargo | Búsqueda → Cargo | Cargo |
| Sede | Opción: Casa matriz, Sucursal | Sede |
| Sucursal | Búsqueda → Sucursal (vacía en casa matriz) | Sucursal |
| Fecha de ingreso | Fecha (Solo fecha) | FechaIngreso |
| Jefatura | Texto | Jefatura |
| Tutor | Texto | Tutor |
| Fecha de registro | Fecha (Solo fecha) | FechaRegistro |
| Días de anticipación | Número entero | DiasAnticipacion |
| Estado ingreso | Opción: Programado, En curso, Completado, Cancelado | Estado |

La columna `Area` del CSV no se importa (el Área sale del Cargo).

### Tarea de onboarding — `TareasOnboarding.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| ID tarea | **Principal** (texto) | TareaID |
| Ingreso | Búsqueda → Ingreso | IngresoID |
| Plantilla | Búsqueda → Plantilla de tarea | CodigoTarea |
| Tarea | Texto | Tarea |
| Fase | Opción (las mismas de Plantilla de tarea) | Fase |
| Responsable | Opción (las mismas de Plantilla de tarea) | Responsable |
| Asignado a | Texto | AsignadoA |
| Fecha de compromiso | Fecha (Solo fecha) | FechaCompromiso |
| Fecha completado | Fecha (Solo fecha) | FechaCompletado |
| Estado tarea | Opción: Pendiente, Completada | Estado |
| Comentario | Texto multilínea | Comentario |

### Encuesta de onboarding — `EncuestaOnboarding.csv`
| Columna | Tipo | Columna del CSV |
|---|---|---|
| ID encuesta | **Principal** (texto) | EncuestaID |
| Ingreso | Búsqueda → Ingreso | IngresoID |
| Fecha de respuesta | Fecha (Solo fecha) | FechaRespuesta |
| Satisfacción general | Número entero (1 a 5) | SatisfaccionGeneral |
| Claridad del primer día | Número entero (1 a 5) | ClaridadPrimerDia |
| Equipo listo el día 1 | Opción: Sí, No | EquipoListoDia1 |
| Comentario | Texto multilínea | Comentario |

## Tip: opciones globales

Fase, Rol responsable, Sede y Sí/No se repiten en varias tablas. Conviene crearlas una vez como **opciones globales** dentro de la solución y reutilizarlas: si cambian, se cambian en un solo lugar.

## Nombres que conviene evitar

Toda tabla de Dataverse trae columnas de sistema, entre ellas **Estado** y **Razón para el estado** (activo/inactivo). Por eso las columnas propias se llaman **Estado ingreso** y **Estado tarea**, para no confundirse con ellas.
