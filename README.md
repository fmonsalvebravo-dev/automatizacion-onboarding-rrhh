# Automatización del onboarding de nuevos colaboradores

Proyecto de portafolio: automatización del proceso de onboarding de una empresa ficticia, **Austral Servicios Financieros S.A.** (~600 colaboradores, casa matriz en Santiago y 12 sucursales), con Microsoft Power Platform.

> En construcción. Este README se completa a medida que avanza el proyecto.

## Stack

- **Dataverse**: base de datos relacional (8 tablas dentro de una solución)
- **Power Apps**: app para que Personas registre ingresos y siga su avance
- **Power Automate**: creación de tareas, avisos y recordatorios por atraso
- **Power BI**: dashboard de cumplimiento y experiencia de onboarding
- **Copilot Studio**: agente que responde las preguntas de los nuevos colaboradores
- **Python (pandas)**: generación del histórico sintético

## El proceso

Cuando Personas registra un ingreso, se crean automáticamente 14 tareas para TI, Administración, Personas, la jefatura, el tutor y el propio colaborador, cada una con su fecha de compromiso (fecha de ingreso + día relativo). El proceso va desde 10 días antes del ingreso hasta la evaluación del período de prueba (día 85).

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `docs/` | Documento de diseño y capturas |
| `datos/` | Script generador del histórico y CSV resultantes |
| `dataverse/` | Modelo de datos, relaciones y orden de importación |
| `power-platform/` | Solución exportada (app, flujos y agente) |
| `power-bi/` | Archivo del dashboard |
| `copilot-studio/` | Base de conocimiento del agente |

## Avance

- [x] Paso 1: diseño del proceso y modelo de datos
- [x] Paso 2: histórico sintético (173 ingresos, 2.352 tareas, mayo 2025 a octubre 2026)
- [ ] Paso 3: tablas en Dataverse
- [ ] Paso 4: Power App
- [ ] Paso 5: flujos de Power Automate
- [ ] Paso 6: dashboard en Power BI
- [ ] Paso 7: agente en Copilot Studio
- [ ] Paso 8: video demo

## Cómo regenerar los datos

```bash
pip install pandas numpy
python datos/generar_historico.py
```

Usa una semilla fija, por lo que siempre genera los mismos datos.
