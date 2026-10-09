# 🚚 DeliverTrack — Sistema de control y seguimiento de entregas

Aplicación web que transforma digitalmente el proceso de despacho de una pequeña
empresa de entregas que hoy controla sus pedidos por WhatsApp, llamadas y notas
sueltas: pedidos pendientes perdidos, entregas retrasadas sin aviso y cero
trazabilidad de quién hizo qué.

**Proyecto académico** — Tecnología de la Información · Unidad I · Fundamentos y
transformación digital.

## ¿Qué resuelve?

| Problema del proceso actual | Solución en DeliverTrack |
|---|---|
| No se sabe qué pedidos están pendientes o enviados | Estados controlados: `RECIBIDO → PREPARANDO → ASIGNADO → EN CAMINO → ENTREGADO` |
| Entregas que se retrasan y nadie lo nota a tiempo | **Automatización**: clasificación 🟢 normal / 🟡 en riesgo (≤ 30 min para la hora límite) / 🔴 retrasada + alertas al supervisor |
| Decisiones basadas solo en la experiencia | Tablero y analítica: % de puntualidad, tiempo promedio, retrasos, incidencias por tipo y rendimiento por repartidor |
| Sin registro de quién hizo cada operación | Historial de trazabilidad: usuario, fecha, acción y resultado de cada operación importante |
| Cada quien hace lo que puede con lo que tiene | Dos roles con permisos diferenciados: **Administrador** y **Repartidor** |

## Ecosistema tecnológico

- **Frontend:** React 18 + Vite + Chart.js
- **Backend:** Django 6 + Django REST Framework + JWT (SimpleJWT)
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (nube, vía `DATABASE_URL`)
- **Tecnologías habilitadoras:** computación en la nube + analítica de datos
  (justificación completa en [`docs/06-tecnologias-habilitadoras.md`](docs/06-tecnologias-habilitadoras.md))

## Estructura del repositorio

```
delivertrack/
├── backend/            # API Django REST (apps: accounts, operations, analytics)
│   ├── config/         # Ajustes y rutas (lee variables de entorno)
│   ├── apps/accounts/  # Usuarios, roles y repartidores
│   ├── apps/operations/# Pedidos, entregas, incidencias, historial, alertas
│   ├── apps/analytics/ # Endpoints de analítica para el tablero
│   └── tests/          # Pruebas automatizadas (pytest)
├── frontend/           # SPA React (login, tablero, pedidos, mis entregas, analítica)
├── docs/               # Entregables 1, 2 y 4 (propuesta, diseño, matrices)
├── deploy/             # Configuración de despliegue en la nube (Render)
└── docker-compose.yml  # Ejecución con PostgreSQL como en producción
```

## Requisitos

- Python 3.12+ y Node.js 18+ (probado con Node 22)
- No se necesita PostgreSQL para la demo: SQLite está incluido.

## Instalación y ejecución (backend)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # datos sintéticos de demostración
python manage.py runserver          # API en http://127.0.0.1:8000
```

## Instalación y ejecución (frontend)

```bash
cd frontend
npm install
npm run dev                         # App en http://localhost:5173 (proxia /api al 8000)
```

## Usuarios de demostración (creados por `seed_demo`)

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Demo1234!` | Administrador |
| `carlos` | `Demo1234!` | Repartidor |
| `maria` | `Demo1234!` | Repartidor |
| `pedro` | `Demo1234!` | Repartidor |

> ⚠️ Contraseñas solo para la demostración; cámbielas en un entorno real.

## Guion de demostración (10 minutos)

1. **Login como `admin`** → tablero: contadores, alertas activas y entregas
   activas con semáforo de riesgo. La lista ya incluye una entrega 🟡 *en
   riesgo* (quedan ~20 min) y una 🔴 *retrasada* generadas por la automatización.
2. **Pedidos**: registrar un pedido nuevo con hora límite a 40 minutos;
   pasarlo a `Preparando` y asignarlo a un repartidor.
3. **Login como repartidor** (`maria`) → *Mis entregas*: ver dirección y hora
   límite, `Registrar salida` → `En camino`, y `Marcar entregada`.
4. Volver a `admin` → la entrega aparece cerrada, las alertas desaparecen y el
   historial muestra cada operación (usuario, fecha, acción, resultado).
5. **Analítica**: % de entregas a tiempo, tiempo promedio, serie diaria,
   rendimiento por repartidor y causas de incidencias.
6. **Comando de automatización** (opcional): `python manage.py evaluar_riesgos`
   muestra cómo se evalúan las entregas activas sin esperar el tablero.

## Pruebas

```bash
cd backend
python -m pytest        # 25 pruebas: validaciones, permisos, reglas y automatización
```

La matriz completa (positivas, negativas, de permisos e indisponibilidad) está
en [`docs/08-matriz-pruebas.md`](docs/08-matriz-pruebas.md).

## Configuración (variables de entorno)

| Variable | Por defecto | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | clave de desarrollo | Clave secreta (obligatoria en producción) |
| `DEBUG` | `1` | Modo depuración; en producción usar `0` |
| `ALLOWED_HOSTS` | `*` | Hosts permitidos separados por coma |
| `DATABASE_URL` | SQLite local | Cadena de conexión (PostgreSQL en la nube) |
| `CORS_ALLOWED_ORIGINS` | — | Origen del frontend permitido |
| `TIME_ZONE` | `America/Managua` | Zona horaria del negocio |
| `RIESGO_MINUTOS` | `30` | Margen de la regla de riesgo (ver `docs/03-flujo-informacion.md`) |
| `EVALUAR_RIESGO_AL_CONSULTAR` | `1` | Evalúa riesgos al consultar el tablero (demo). En producción usar `0` + cron |

Ver `.env.example`. El repositorio no contiene claves ni contraseñas reales.

## Despliegue en la nube

- Ejemplo listo para [Render](https://render.com): `deploy/render.yaml`
  (web service + PostgreSQL gestionada) — ejecución: `docker compose up` local
  con PostgreSQL.
- El frontend puede publicarse en Vercel/Netlify apuntando `CORS_ALLOWED_ORIGINS`
  a su dominio.

## Licencias y atribución

Código propio bajo licencia [MIT](LICENSE). Componentes de terceros: Django
(BSD), Django REST Framework (BSD), SimpleJWT (MIT), React (MIT), Vite (MIT),
Chart.js (MIT), axios (MIT), PostgreSQL (Licencia PostgreSQL).

## Datos

La aplicación **no contiene datos personales reales**: los pedidos y usuarios de
la demo son sintéticos (generados por `seed_demo`), conforme al enunciado.
