# Entregable 2e · Integraciones con tecnologías habilitadoras

El enunciado exige incorporar **al menos dos** de: computación en la nube, IoT,
IA, analítica de datos/Big Data. DeliverTrack incorpora **nube** y **analítica
de datos**, y **justifica** por qué no incorpora las otras dos.

## ☁️ 1. Computación en la nube

| Elemento | Implementación |
|---|---|
| Aplicación desplegada en la nube | Django + Gunicorn, contenedor Docker (`backend/Dockerfile`); plantilla de despliegue en Render (`deploy/render.yaml`) con HTTPS incluido |
| Base de datos en la nube | PostgreSQL gestionada vía `DATABASE_URL` (`docker-compose.yml` replica el esquema en local) |
| API disponible para los usuarios | API REST única consumida por el supervisor (PC) y los repartidores (navegador del teléfono) |
| Acceso multi-dispositivo | El repartidor actualiza su estado desde la ruta sin instalar nada |
| Respaldo y disponibilidad | Los datos viven en el servidor, no en hojas de Excel locales; si un teléfono se pierde, la operación continúa |

**Por qué sí aporta:** el proceso es móvil por naturaleza (repartidores en
ruta) y centralizado en la información (supervisor): la nube es lo que permite
que ambos roles compartan el mismo estado en tiempo real.

## 📊 2. Analítica de datos

El módulo `apps/analytics` convierte los datos operativos en información para
decidir (todo consultable por el administrador):

| Análisis | Endpoint | Decisión que apoya |
|---|---|---|
| % de entregas a tiempo y retrasos | `/api/analitica/kpis/` | Cumplimiento del servicio frente a la línea base (~72 %) |
| Tiempo promedio de entrega | `/api/analitica/kpis/` | Dimensionar cuántos pedidos por hora puede despachar cada repartidor |
| Serie diaria (14 días) | `/api/analitica/entregas-por-dia/` | Días pico → programar refuerzos |
| Entregas a tiempo vs retrasadas | `/api/analitica/puntualidad/` | Comunicar el nivel de servicio |
| Rendimiento por repartidor | `/api/analitica/por-repartidor/` | Asignación de carga equitativa (datos, no memoria) |
| Causas de incidencias | `/api/analitica/incidencias-por-tipo/` | Atacar la causa principal (p. ej. verificar direcciones al registrar) |

Las gráficas (Chart.js) están en la vista *Analítica* del frontend.

## ❌ Por qué NO incorporamos IoT ni IA (justificación exigida)

- **IoT:** no existen equipos físicos que sensorear en este proceso
  (no hay flota GPS instalada ni sensores de frío/temperatura). Simular un
  sensor sería artificioso: los eventos reales del proceso los registran los
  propios usuarios al actualizar estados. Si la empresa instalara GPS en las
  motos, la API ya podría recibirlo (nuevo endpoint), pero hoy no aporta valor.
- **IA / ML:** con ~30 entregas diarias no hay volumen de datos para entrenar
  un modelo, y una regla determinista (riesgo por tiempo restante) es
  **explicable, auditable y suficiente** para el problema. Pretender un
  modelo de predicción de retrasos con estos datos sería "meter IA porque sí",
  sin métrica ni capacidad real de generalización. La evolución natural
  (documentada en el informe) es usar el histórico acumulado por la app para,
  en el futuro, estimar tiempos por zona/horario con datos reales.
