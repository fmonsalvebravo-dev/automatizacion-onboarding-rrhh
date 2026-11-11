"""
Proyecto Onboarding - Paso 2: generador del histórico sintético
================================================================

Genera los datos de la empresa ficticia "Austral Servicios Financieros S.A."
para cargarlos en tablas de Dataverse y analizarlos en Power BI.

Período: ingresos entre mayo 2025 y octubre 2026 (18 meses), más algunos
ingresos programados para nov-dic 2026 (sirven para la demo de la app).
Fecha de corte ("hoy"): 11-11-2026. Lo que vence después de esa fecha
queda Pendiente, igual que en un sistema real.

Patrones escondidos a propósito (para "descubrirlos" en Power BI):
  1. TI se atrasa bastante más en los meses de peak (marzo y agosto).
  2. Las sucursales regionales se atrasan más en equipo y puesto (despachos).
  3. Los ingresos registrados con menos de 5 días de anticipación concentran
     los atrasos y tienen peor satisfacción en la encuesta.

Salida: un CSV por lista en la carpeta "datos/csv/".
Requisitos: pip install pandas numpy
"""

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Configuración general
# ---------------------------------------------------------------------------
SEMILLA = 42                      # misma semilla = mismos datos siempre
rng = np.random.default_rng(SEMILLA)

FECHA_CORTE = date(2026, 11, 11)
MES_INICIO = date(2025, 5, 1)
CANTIDAD_MESES = 18               # mayo 2025 a octubre 2026
MESES_PEAK = {3, 8}               # marzo y agosto
CARPETA_SALIDA = Path(__file__).parent / "csv"   # los CSV quedan en datos/csv/
DOMINIO = "example.com"           # dominio ficticio; en el paso 4 lo cambias por el de tu tenant


# ---------------------------------------------------------------------------
# 1. Listas maestras
# ---------------------------------------------------------------------------
areas = pd.DataFrame([
    {"Area": "Comercial",                  "Jefatura": "Marcela Contreras"},
    {"Area": "Operaciones",                "Jefatura": "Andrés Valenzuela"},
    {"Area": "Riesgo",                     "Jefatura": "Paula Herrera"},
    {"Area": "Tecnología",                 "Jefatura": "Felipe Navarro"},
    {"Area": "Personas",                   "Jefatura": "Daniela Muñoz"},
    {"Area": "Administración y Finanzas",  "Jefatura": "Jorge Espinoza"},
])

cargos = pd.DataFrame([
    # Cargos de sucursal (área Comercial)
    {"Cargo": "Ejecutivo/a de atención",      "Area": "Comercial",   "Sede": "Sucursal"},
    {"Cargo": "Ejecutivo/a comercial",        "Area": "Comercial",   "Sede": "Sucursal"},
    {"Cargo": "Cajero/a",                     "Area": "Comercial",   "Sede": "Sucursal"},
    # Cargos de casa matriz
    {"Cargo": "Analista comercial",           "Area": "Comercial",   "Sede": "Casa matriz"},
    {"Cargo": "Analista de operaciones",      "Area": "Operaciones", "Sede": "Casa matriz"},
    {"Cargo": "Asistente de operaciones",     "Area": "Operaciones", "Sede": "Casa matriz"},
    {"Cargo": "Analista de riesgo",           "Area": "Riesgo",      "Sede": "Casa matriz"},
    {"Cargo": "Analista de cobranza",         "Area": "Riesgo",      "Sede": "Casa matriz"},
    {"Cargo": "Desarrollador/a",              "Area": "Tecnología",  "Sede": "Casa matriz"},
    {"Cargo": "Analista de soporte",          "Area": "Tecnología",  "Sede": "Casa matriz"},
    {"Cargo": "Analista de datos",            "Area": "Tecnología",  "Sede": "Casa matriz"},
    {"Cargo": "Analista de personas",         "Area": "Personas",    "Sede": "Casa matriz"},
    {"Cargo": "Asistente de remuneraciones",  "Area": "Personas",    "Sede": "Casa matriz"},
    {"Cargo": "Analista contable",            "Area": "Administración y Finanzas", "Sede": "Casa matriz"},
    {"Cargo": "Analista de tesorería",        "Area": "Administración y Finanzas", "Sede": "Casa matriz"},
])

sucursales = pd.DataFrame([
    {"Sucursal": "Arica",           "Region": "Arica y Parinacota", "Regional": "Sí", "Jefatura": "Héctor Morales"},
    {"Sucursal": "Iquique",         "Region": "Tarapacá",           "Regional": "Sí", "Jefatura": "Lorena Pizarro"},
    {"Sucursal": "Antofagasta",     "Region": "Antofagasta",        "Regional": "Sí", "Jefatura": "Cristián Araya"},
    {"Sucursal": "Calama",          "Region": "Antofagasta",        "Regional": "Sí", "Jefatura": "Verónica Tapia"},
    {"Sucursal": "La Serena",       "Region": "Coquimbo",           "Regional": "Sí", "Jefatura": "Rodrigo Castillo"},
    {"Sucursal": "Viña del Mar",    "Region": "Valparaíso",         "Regional": "Sí", "Jefatura": "Francisca Vega"},
    {"Sucursal": "Santiago Centro", "Region": "Metropolitana",      "Regional": "No", "Jefatura": "Gonzalo Reyes"},
    {"Sucursal": "Puente Alto",     "Region": "Metropolitana",      "Regional": "No", "Jefatura": "Claudia Sepúlveda"},
    {"Sucursal": "Rancagua",        "Region": "O'Higgins",          "Regional": "Sí", "Jefatura": "Mauricio Flores"},
    {"Sucursal": "Talca",           "Region": "Maule",              "Regional": "Sí", "Jefatura": "Natalia Bravo"},
    {"Sucursal": "Concepción",      "Region": "Biobío",             "Regional": "Sí", "Jefatura": "Sebastián Fuentes"},
    {"Sucursal": "Puerto Montt",    "Region": "Los Lagos",          "Regional": "Sí", "Jefatura": "Ignacia Cárdenas"},
])

responsables = pd.DataFrame([
    {"Rol": "TI",             "PersonaAsignada": "Mesa de Ayuda TI", "Correo": f"mesadeayuda@{DOMINIO}"},
    {"Rol": "Personas",       "PersonaAsignada": "Carolina Rojas",   "Correo": f"carolina.rojas@{DOMINIO}"},
    {"Rol": "Administración", "PersonaAsignada": "Patricio Soto",    "Correo": f"patricio.soto@{DOMINIO}"},
])

plantilla = pd.DataFrame([
    # Codigo, Tarea, Responsable, DiaRelativo, Fase, AplicaA
    ("T01", "Preparar y enviar contrato",                "Personas",       -7, "Pre-ingreso",    "Todos"),
    ("T02", "Crear cuenta y correo corporativo",         "TI",             -3, "Pre-ingreso",    "Todos"),
    ("T03", "Preparar y configurar notebook",            "TI",             -2, "Pre-ingreso",    "Casa matriz"),
    ("T04", "Habilitar estación de atención en sucursal","TI",             -2, "Pre-ingreso",    "Sucursal"),
    ("T05", "Asignar puesto y credencial de acceso",     "Administración", -1, "Pre-ingreso",    "Todos"),
    ("T06", "Asignar tutor",                             "Jefatura",       -1, "Pre-ingreso",    "Todos"),
    ("T07", "Bienvenida y entrega de equipo",            "Jefatura",        0, "Primer día",     "Todos"),
    ("T08", "Inducción corporativa",                     "Personas",        0, "Primer día",     "Todos"),
    ("T09", "Accesos a sistemas del área",               "TI",              2, "Primera semana", "Todos"),
    ("T10", "Inducción del cargo",                       "Tutor",           3, "Primera semana", "Todos"),
    ("T11", "Curso de prevención de lavado de activos",  "Colaborador",    15, "Primer mes",     "Todos"),
    ("T12", "Curso de seguridad de la información",      "Colaborador",    15, "Primer mes",     "Todos"),
    ("T13", "Reunión de seguimiento a 30 días",          "Jefatura",       30, "Primer mes",     "Todos"),
    ("T14", "Encuesta de experiencia de onboarding",     "Colaborador",    30, "Primer mes",     "Todos"),
    ("T15", "Evaluación de período de prueba",           "Jefatura",       85, "Cierre",         "Todos"),
], columns=["Codigo", "Tarea", "Responsable", "DiaRelativo", "Fase", "AplicaA"])
plantilla["Activa"] = "Sí"

# Correos de jefaturas (ficticios)
def correo_de(nombre_completo: str) -> str:
    """'Marcela Contreras' -> 'marcela.contreras@example.com' (sin tildes)."""
    tabla = str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN")
    partes = nombre_completo.translate(tabla).lower().split()
    return f"{partes[0]}.{partes[-1]}@{DOMINIO}"

areas["CorreoJefatura"] = areas["Jefatura"].apply(correo_de)
sucursales["CorreoJefatura"] = sucursales["Jefatura"].apply(correo_de)


# ---------------------------------------------------------------------------
# 2. Funciones de apoyo
# ---------------------------------------------------------------------------
NOMBRES = ["Camila", "Valentina", "Javiera", "Constanza", "Catalina", "Fernanda",
           "Isidora", "Antonia", "Martina", "Josefa", "Bárbara", "Macarena",
           "Tamara", "Paulina", "Karina", "Daniela", "Benjamín", "Matías",
           "Vicente", "Tomás", "Joaquín", "Diego", "Nicolás", "Ignacio",
           "Cristóbal", "Felipe", "Sebastián", "Martín", "Agustín", "Lucas",
           "Bastián", "Esteban", "Rodrigo", "Pablo", "Álvaro", "Gabriel"]
APELLIDOS = ["González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras",
             "Silva", "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López",
             "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza",
             "Valenzuela", "Castillo", "Tapia", "Reyes", "Gutiérrez", "Castro",
             "Pizarro", "Álvarez", "Vásquez", "Sánchez", "Fernández", "Ramírez",
             "Carrasco", "Gómez", "Cortés", "Herrera", "Núñez"]

def nombre_aleatorio() -> str:
    return f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"

def siguiente_dia_habil(d: date) -> date:
    """Si cae sábado o domingo, lo mueve al lunes."""
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d

def dia_habil_aleatorio(anio: int, mes: int) -> date:
    """Un día hábil al azar dentro del mes."""
    primero = date(anio, mes, 1)
    siguiente = date(anio + (mes == 12), mes % 12 + 1, 1)
    dias = [primero + timedelta(days=i) for i in range((siguiente - primero).days)]
    habiles = [d for d in dias if d.weekday() < 5]
    return habiles[rng.integers(len(habiles))]

def meses_del_periodo():
    anio, mes = MES_INICIO.year, MES_INICIO.month
    for _ in range(CANTIDAD_MESES):
        yield anio, mes
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)


# ---------------------------------------------------------------------------
# 3. Ingresos
# ---------------------------------------------------------------------------
def dias_de_anticipacion() -> int:
    """Con cuántos días de anticipación Personas registra el ingreso.
    ~60 % lo hace bien (8-15 días), ~25 % justo (5-7) y ~15 % tarde (1-4)."""
    r = rng.random()
    if r < 0.60:
        return int(rng.integers(8, 16))
    if r < 0.85:
        return int(rng.integers(5, 8))
    return int(rng.integers(1, 5))

def crear_ingreso(fecha_ingreso: date) -> dict:
    # La mitad de los ingresos son de sucursal (Comercial), el resto de casa matriz
    if rng.random() < 0.5:
        cargo = cargos[cargos["Sede"] == "Sucursal"].sample(1, random_state=rng).iloc[0]
        suc = sucursales.sample(1, random_state=rng).iloc[0]
        sucursal, jefatura = suc["Sucursal"], suc["Jefatura"]
    else:
        cargo = cargos[cargos["Sede"] == "Casa matriz"].sample(1, random_state=rng).iloc[0]
        sucursal = ""
        jefatura = areas.loc[areas["Area"] == cargo["Area"], "Jefatura"].iloc[0]

    nombre = nombre_aleatorio()
    anticipacion = dias_de_anticipacion()
    return {
        "Nombre": nombre,
        "CorreoPersonal": correo_de(nombre).replace(DOMINIO, f"personal.{DOMINIO}"),
        "Cargo": cargo["Cargo"],
        "Area": cargo["Area"],
        "Sede": cargo["Sede"],
        "Sucursal": sucursal,
        "FechaIngreso": fecha_ingreso,
        "Jefatura": jefatura,
        "Tutor": nombre_aleatorio(),
        "FechaRegistro": fecha_ingreso - timedelta(days=anticipacion),
        "DiasAnticipacion": anticipacion,   # útil para el análisis; en la app se calcula
    }

filas = []
for anio, mes in meses_del_periodo():
    cantidad = int(rng.integers(12, 15)) if mes in MESES_PEAK else int(rng.integers(7, 11))
    for _ in range(cantidad):
        filas.append(crear_ingreso(dia_habil_aleatorio(anio, mes)))

# Algunos ingresos futuros ya registrados (para ver "Programado" en la app)
for fecha in [date(2026, 11, 16), date(2026, 11, 23), date(2026, 11, 30),
              date(2026, 12, 1), date(2026, 12, 7)]:
    ingreso = crear_ingreso(fecha)
    ingreso["DiasAnticipacion"] = max(ingreso["DiasAnticipacion"], (fecha - FECHA_CORTE).days + 1)
    ingreso["FechaRegistro"] = fecha - timedelta(days=ingreso["DiasAnticipacion"])
    filas.append(ingreso)

ingresos = pd.DataFrame(filas).sort_values("FechaIngreso").reset_index(drop=True)
ingresos.insert(0, "IngresoID", [f"ING-{i:04d}" for i in range(1, len(ingresos) + 1)])

# ~3 % de los ingresos pasados se cancelan (la persona no llegó)
pasados = ingresos["FechaIngreso"] <= FECHA_CORTE
cancelados = pasados & (rng.random(len(ingresos)) < 0.03)


# ---------------------------------------------------------------------------
# 4. Tareas de onboarding (el corazón de los patrones)
# ---------------------------------------------------------------------------
def simular_dias_de_atraso(tarea, ingreso) -> int:
    """Devuelve cuántos días después del compromiso se completó la tarea
    (negativo = se hizo antes). Aquí viven los tres patrones."""
    prob_atraso, atraso_medio = 0.10, 2.0
    regional = sucursales.set_index("Sucursal")["Regional"].get(ingreso["Sucursal"], "No") == "Sí"
    tardio = ingreso["DiasAnticipacion"] < 5

    if tarea["Responsable"] == "TI":
        prob_atraso, atraso_medio = 0.12, 2.0
        if ingreso["FechaIngreso"].month in MESES_PEAK:          # Patrón 1
            prob_atraso, atraso_medio = 0.50, 4.0
    if tarea["Codigo"] in ("T04", "T05") and regional:           # Patrón 2
        prob_atraso += 0.30
        atraso_medio += 3.0
    if tardio and tarea["DiaRelativo"] <= 0:                     # Patrón 3
        prob_atraso += 0.30
        atraso_medio += 2.0
    if tarea["Responsable"] == "Colaborador" and tarea["Codigo"] != "T14":
        prob_atraso, atraso_medio = 0.30, 5.0                    # cursos e-learning
    if tarea["Codigo"] in ("T13", "T15"):
        prob_atraso, atraso_medio = 0.25, 6.0                    # agendas de jefatura

    if rng.random() < min(prob_atraso, 0.9):
        return 1 + int(rng.poisson(atraso_medio))
    # A tiempo: las tareas previas a veces se adelantan
    return int(rng.integers(-3, 1)) if tarea["DiaRelativo"] < 0 else int(rng.integers(-1, 1))

def asignado_a(rol: str, ingreso) -> str:
    if rol == "Jefatura":
        return ingreso["Jefatura"]
    if rol == "Tutor":
        return ingreso["Tutor"]
    if rol == "Colaborador":
        return ingreso["Nombre"]
    return responsables.loc[responsables["Rol"] == rol, "PersonaAsignada"].iloc[0]

tareas = []
for idx, ing in ingresos.iterrows():
    if cancelados[idx]:
        continue   # un ingreso cancelado no genera tareas
    for _, t in plantilla.iterrows():
        if t["AplicaA"] not in ("Todos", ing["Sede"]):
            continue
        # Regla de negocio (la misma que usará el flujo): fecha ingreso + día relativo
        compromiso = ing["FechaIngreso"] + timedelta(days=int(t["DiaRelativo"]))
        completado = compromiso + timedelta(days=simular_dias_de_atraso(t, ing))
        # Nadie puede completar una tarea antes de que el ingreso exista en el sistema
        if completado < ing["FechaRegistro"]:
            completado = ing["FechaRegistro"] + timedelta(days=int(rng.integers(0, 2)))
        completado = siguiente_dia_habil(completado)

        terminada = completado <= FECHA_CORTE
        tareas.append({
            "IngresoID": ing["IngresoID"],
            "CodigoTarea": t["Codigo"],
            "Tarea": t["Tarea"],
            "Fase": t["Fase"],
            "Responsable": t["Responsable"],
            "AsignadoA": asignado_a(t["Responsable"], ing),
            "FechaCompromiso": compromiso,
            "FechaCompletado": completado if terminada else None,
            "Estado": "Completada" if terminada else "Pendiente",
            "Comentario": "",
        })

tareas = pd.DataFrame(tareas)
tareas.insert(0, "TareaID", [f"TAR-{i:05d}" for i in range(1, len(tareas) + 1)])

# Estado de cada ingreso según sus tareas
pendientes = tareas[tareas["Estado"] == "Pendiente"].groupby("IngresoID").size()
def estado_ingreso(row) -> str:
    if row["IngresoID"] in set(ingresos.loc[cancelados, "IngresoID"]):
        return "Cancelado"
    if row["FechaIngreso"] > FECHA_CORTE:
        return "Programado"
    return "En curso" if pendientes.get(row["IngresoID"], 0) > 0 else "Completado"

ingresos["Estado"] = ingresos.apply(estado_ingreso, axis=1)


# ---------------------------------------------------------------------------
# 5. Encuesta de onboarding a 30 días
# ---------------------------------------------------------------------------
COMENTARIOS = {
    "alto":  ["Todo estuvo listo desde el primer día.",
              "Muy buena inducción, me sentí bienvenido/a.",
              "Mi tutor me ayudó mucho la primera semana."],
    "medio": ["En general bien, aunque algunos accesos tardaron.",
              "La inducción fue útil, pero con mucha información junta."],
    "bajo":  ["El primer día no tenía equipo para trabajar.",
              "Pasé varios días sin acceso a los sistemas.",
              "Sentí que no me estaban esperando."],
}

t_idx = tareas.set_index(["IngresoID", "CodigoTarea"])
encuestas = []
for _, ing in ingresos.iterrows():
    clave = (ing["IngresoID"], "T14")
    if clave not in t_idx.index or t_idx.loc[clave, "Estado"] != "Completada":
        continue
    if rng.random() > 0.85:      # ~85 % responde
        continue

    propias = tareas[tareas["IngresoID"] == ing["IngresoID"]]
    primeras = propias[propias["CodigoTarea"].isin(["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"])]
    atrasos_inicio = int((primeras["FechaCompletado"] > primeras["FechaCompromiso"]).sum())
    equipo = propias[propias["CodigoTarea"].isin(["T03", "T04"])].iloc[0]
    equipo_listo = equipo["FechaCompletado"] <= ing["FechaIngreso"]
    tardio = ing["DiasAnticipacion"] < 5

    satisf = 4.7 - 0.35 * atrasos_inicio - (0 if equipo_listo else 0.8) - (0.4 if tardio else 0)
    claridad = 4.6 - 0.30 * atrasos_inicio - (0 if equipo_listo else 0.6)
    satisf = int(np.clip(round(satisf + rng.normal(0, 0.45)), 1, 5))
    claridad = int(np.clip(round(claridad + rng.normal(0, 0.45)), 1, 5))

    nivel = "alto" if satisf >= 4 else ("medio" if satisf == 3 else "bajo")
    comentario = str(rng.choice(COMENTARIOS[nivel])) if rng.random() < 0.5 else ""

    encuestas.append({
        "IngresoID": ing["IngresoID"],
        "FechaRespuesta": t_idx.loc[clave, "FechaCompletado"],
        "SatisfaccionGeneral": satisf,
        "ClaridadPrimerDia": claridad,
        "EquipoListoDia1": "Sí" if equipo_listo else "No",
        "Comentario": comentario,
    })
encuestas = pd.DataFrame(encuestas)
# ID propio de la encuesta (columna principal en Dataverse); IngresoID queda como búsqueda
encuestas.insert(0, "EncuestaID", [f"ENC-{i:04d}" for i in range(1, len(encuestas) + 1)])


# ---------------------------------------------------------------------------
# 6. Guardar CSV (utf-8-sig para que Excel muestre bien las tildes)
# ---------------------------------------------------------------------------
CARPETA_SALIDA.mkdir(exist_ok=True)
salidas = {
    "Areas": areas, "Cargos": cargos, "Sucursales": sucursales,
    "Responsables": responsables, "PlantillaTareas": plantilla,
    "Ingresos": ingresos, "TareasOnboarding": tareas, "EncuestaOnboarding": encuestas,
}
for nombre, df in salidas.items():
    df.to_csv(CARPETA_SALIDA / f"{nombre}.csv", index=False, encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# 7. Verificación rápida de que los patrones quedaron en los datos
# ---------------------------------------------------------------------------
def pct_a_tiempo(df) -> str:
    hechas = df[df["Estado"] == "Completada"]
    return f"{(hechas['FechaCompletado'] <= hechas['FechaCompromiso']).mean():.0%}"

tc = tareas.merge(ingresos[["IngresoID", "FechaIngreso", "Sucursal", "DiasAnticipacion"]], on="IngresoID")
tc["MesPeak"] = tc["FechaIngreso"].apply(lambda d: d.month in MESES_PEAK)
tc = tc.merge(sucursales[["Sucursal", "Regional"]], on="Sucursal", how="left")

print("Resumen de lo generado")
for nombre, df in salidas.items():
    print(f"  {nombre:<20} {len(df):>5} filas")
print("\nEstados de ingresos:", ingresos["Estado"].value_counts().to_dict())

print("\n% de tareas a tiempo por responsable:")
for rol, grupo in tc.groupby("Responsable"):
    print(f"  {rol:<15} {pct_a_tiempo(grupo)}")

ti = tc[tc["Responsable"] == "TI"]
print(f"\nPatrón 1 - TI a tiempo: meses peak {pct_a_tiempo(ti[ti['MesPeak']])} vs resto {pct_a_tiempo(ti[~ti['MesPeak']])}")

eq = tc[tc["CodigoTarea"].isin(["T04", "T05"]) & (tc["Sucursal"] != "")]
print(f"Patrón 2 - Equipo/puesto en sucursal a tiempo: regional {pct_a_tiempo(eq[eq['Regional'] == 'Sí'])} "
      f"vs Santiago {pct_a_tiempo(eq[eq['Regional'] == 'No'])}")

tardio = tc["DiasAnticipacion"] < 5
print(f"Patrón 3 - Tareas a tiempo: registro tardío {pct_a_tiempo(tc[tardio])} vs a tiempo {pct_a_tiempo(tc[~tardio])}")
enc = encuestas.merge(ingresos[["IngresoID", "DiasAnticipacion"]], on="IngresoID")
print(f"           Satisfacción promedio: tardío {enc[enc['DiasAnticipacion'] < 5]['SatisfaccionGeneral'].mean():.1f} "
      f"vs a tiempo {enc[enc['DiasAnticipacion'] >= 5]['SatisfaccionGeneral'].mean():.1f}")
