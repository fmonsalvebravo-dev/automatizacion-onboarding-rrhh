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

## Los datos

El histórico es sintético y se genera con Python: **173 ingresos, 2.352 tareas y 136 encuestas** entre mayo 2025 y octubre 2026. Incluye patrones simulados a propósito para descubrirlos en el dashboard:

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
- [ ] Paso 4: app de lienzo para registrar ingresos
- [ ] Paso 5: flujos de Power Automate
- [ ] Paso 6: dashboard en Power BI
- [ ] Paso 7: agente en Copilot Studio
- [ ] Paso 8: video demo

## Desafíos y aprendizajes

- **De SharePoint a Dataverse.** El diseño original usaba listas de SharePoint, pero el tenant de desarrollo no incluye SharePoint. Se migró el modelo a Dataverse, lo que permitió usar relaciones reales (columnas de búsqueda) en vez de claves de texto.
- **Validación de datos en el origen.** Al revisar reglas de negocio sobre el histórico se detectó que 47 de 173 registros caían en fin de semana. Se corrigió en el generador (el registro pasa al viernes anterior) y se agregaron validaciones: ningún registro posterior al ingreso ni a la fecha de corte, y días de anticipación coherentes con las fechas.
- **Fechas y zona horaria.** Las columnas de fecha usan el comportamiento *Solo fecha*; con el valor por defecto (*Usuario local*) Dataverse guarda en UTC y en Chile las fechas pueden aparecer un día antes.
- **Dos importadores, dos comportamientos.** El importador moderno de Excel/CSV cargó bien las tablas sin búsquedas, pero en las tablas con búsquedas fallaba sin mostrar errores. La causa: cada tabla tiene un identificador único con el mismo nombre para mostrar que la tabla (por ejemplo, dos columnas "Cargo"). Se resolvió con el importador clásico desde la app basada en modelo, que permite elegir el destino de cada columna, resuelve las búsquedas por la columna principal y deja un registro de errores por fila.
- **Nombres que chocan con columnas de sistema.** Toda tabla trae columnas *Estado* y *Razón para el estado*, por eso las columnas propias se llaman *Estado ingreso* y *Estado tarea*.

## Cómo regenerar los datos

```bash
python -m pip install -r requirements.txt
python datos/generar_historico.py
```

Usa una semilla fija, por lo que siempre genera los mismos datos. Al final imprime un resumen que permite verificar que los patrones quedaron en los datos.
