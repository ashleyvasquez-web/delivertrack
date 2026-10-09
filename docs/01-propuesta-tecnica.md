# Entregable 1 · Propuesta técnica

**Proyecto:** DeliverTrack — Sistema inteligente de control y seguimiento de entregas
**Curso:** Tecnología de la Información · Unidad I · Fundamentos y transformación digital

## 1. Contexto de la organización y descripción del proceso

Organización estudiada: **pequeña empresa de entregas locales** (comercios que
despachan pedidos a domicilio con 3 repartidores en motocicleta y un panel
liviano). Por confidencialidad no se identifica el nombre comercial; el estudio
se realizó con observación del proceso y una entrevista breve con la
encargada de despacho, **sin recopilar datos personales reales**. Cuando fue
necesario, se usaron **datos sintéticos** que representan el proceso observado.

Proceso actual (AS-IS):

1. Los pedidos llegan por WhatsApp, llamada o directamente en el local.
2. La encargada los apunta en un cuaderno o en una hoja de Excel compartida.
3. Asigna cada entrega a un repartidor "de oídas" o por memoria
   (quién está libre, quién anda cerca).
4. El repartidor avisa por WhatsApp cuando sale y cuando entrega.
5. Los reclamos ("¿dónde está mi pedido?") se atienden llamando a todos.

## 2. Problema, usuarios, alcance y restricciones

**Problema delimitado:** el control del despacho depende de la memoria y de
mensajes sueltos; el negocio no puede saber en tiempo real qué pedidos están
pendientes, qué entregas van retrasadas, quién tiene cada paquete ni cuánto
tarda cada entrega. Esto produce retrasos no detectados, errores de registro y
poca trazabilidad para decisiones.

**Usuarios (2 roles):**

| Rol | Responsabilidades en la app |
|---|---|
| **Administrador / Supervisor** | Registra pedidos, asigna entregas, consulta el tablero y la analítica, atiende alertas y resuelve incidencias |
| **Repartidor** | Consulta sus entregas asignadas (dirección, hora límite), registra salida, marca entrega realizada y reporta problemas |

**Alcance del prototipo:** ciclo completo pedido → entrega para un solo punto
de venta, con automatización de riesgo, tablero, analítica y trazabilidad.
**Fuera de alcance (limitaciones declaradas):** facturación, cobros,
integración con plataformas de mensajería, app nativa para teléfonos y
seguimiento GPS en tiempo real.

**Restricciones:** presupuesto nulo (capas gratuitas), conectividad móvil
variable de los repartidores, sin datos personales reales, tiempo de práctica
acotado.

## 3. Línea base e indicadores

Línea base medida/estimada en el diagnóstico (proceso actual, sin sistema):

| Indicador | Línea base (proceso actual) | Meta con DeliverTrack |
|---|---|---|
| 1. Entregas a tiempo | ~72 % (estimado por la encargada; no existe registro) | Medible y ≥ 90 % |
| 2. Tiempo de registro de un pedido | 3–5 min (cuaderno/Excel + dudas) | < 1 min (formulario único con validaciones) |
| 3. Trazabilidad de operaciones | 0 % (no hay registro de quién hizo qué) | 100 % de los cambios de estado registrados |
| 4. Detección oportuna de retrasos | Reactiva: al reclamar el cliente | Proactiva: alerta ≥ 30 min antes de la hora límite |

La aplicación mide los indicadores 1–3 directamente (`/api/analitica/kpis/`);
el 4 se demuestra con la alerta y el campo `minutos_restantes`.

## 4. Alternativas de ecosistema consideradas y justificación

| Criterio | A) Web en la nube (elegida) | B) App móvil nativa | C) Escritorio local |
|---|---|---|---|
| Usuarios (oficina + ruta) | Acceso desde cualquier dispositivo con navegador | Mejor para notificaciones push | Solo la computadora donde se instala |
| Conectividad en ruta | Si no hay señal, el repartidor actualiza al reconectar (los datos quedan en la base) | Igual, pero requiere tienda de aplicaciones | Requiere sincronización propia |
| Costos | Capa gratuita (Render/Vercel) | Costos de publicación y mantenimiento | Licencias de escritorio |
| Seguridad | HTTPS + JWT + roles centralizados | Igual + superficie de ataque mayor | Datos atrapados en una PC |
| Escalabilidad | Horizontal en la nube | Requiere servidores aparte igual | Ninguna |
| Restricciones del equipo | React/Django ya conocidos | Android/iOS: curva alta para el tiempo disponible | Obsoleto frente al proceso móvil |

**Selección:** aplicación **web en la nube**. Los repartidores solo necesitan
el navegador del teléfono; el supervisor necesita el tablero en la oficina;
la nube da disponibilidad, respaldo y una API única. Se justifica no usar IoT
(no hay equipos físicos que sensorear en este proceso) ni IA/ML de modelos
entrenados (con ~30 entregas/día una regla de negocio determinista es
predecible, explicable y suficiente; ver `docs/06-tecnologias-habilitadoras.md`).

## 5. Requisitos funcionales (priorizados)

| ID | Requisito | Prioridad |
|---|---|---|
| RF-1 | Autenticación con usuario y contraseña (JWT) | Alta |
| RF-2 | Roles: administrador y repartidor, con permisos diferenciados | Alta |
| RF-3 | Registro de pedidos con cliente, dirección, notas y hora límite | Alta |
| RF-4 | Flujo de estados: RECIBIDO → PREPARANDO → ASIGNADO → EN CAMINO → ENTREGADO (+ CANCELADO, INCIDENCIA) | Alta |
| RF-5 | Asignación de entrega a repartidor | Alta |
| RF-6 | Reporte de incidencias con tipo y descripción; resolución por el supervisor | Alta |
| RF-7 | **Automatización:** clasificación 🟢/🟡/🔴 por tiempo restante + alertas | Alta |
| RF-8 | Tablero con contadores y entregas activas | Alta |
| RF-9 | Analítica: % a tiempo, tiempo promedio, serie diaria, por repartidor, incidencias por tipo | Media |
| RF-10 | Historial de trazabilidad (usuario, fecha, acción, resultado) | Alta |

Requisitos no funcionales: contraseñas cifradas ( nunca en texto plano),
validación de datos en frontend y backend, mensajes de error comprensibles,
tiempo de respuesta < 1 s para la demo, código reproducible con
instrucciones y sin claves en el repositorio.

## 6. Riesgos iniciales, consideraciones éticas y tratamiento de datos

- **Privacidad:** no se registran datos personales reales; los datos de demo
  son sintéticos. La dirección del cliente es necesaria para operar y se
  muestra solo a los roles que la necesitan.
- **Seguridad:** JWT con expiración, autorización por rol en cada endpoint,
  contraseñas con cifrado fuerte (PBKDF2 de Django). Riesgo residual: el
  almacenamiento del token en el navegador (aceptado para el prototipo; en
  producción, cookies httpOnly).
- **Sesgo del modelo de riesgo:** la regla es determinista y sus límites están
  documentados; puede equivocarse si el repartidor no actualiza su estado
  (se registra esa limitación en `docs/03-flujo-informacion.md`).
- **Uso responsable de IA:** no se usan modelos de IA que tomen decisiones
  automáticas sobre personas; la clasificación solo sugiere atención.
- **Dependencia tecnológica:** si la nube falla, el negocio puede volver al
  proceso manual; la base de datos es exportable.
- **Propiedad intelectual:** código propio con licencia MIT; dependencias de
  terceros listadas en el README con sus licencias.
