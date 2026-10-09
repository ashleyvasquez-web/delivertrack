# Entregable 2b · Flujo de información: dato → decisión → acción → retroalimentación

Recorrido completo con un ejemplo real de la demo (los valores coinciden con
los datos sintéticos generados por `seed_demo`):

| Etapa | Quién / qué | Ejemplo concreto |
|---|---|---|
| **1. DATO** (captura) | El supervisor registra el pedido; el repartidor registra la salida | Pedido #025 · "Ferretería El Buen Precio" · hora límite 4:00 PM · salida 2:00 PM · estado EN CAMINO |
| **2. INFORMACIÓN** (proceso) | El sistema calcula con los datos almacenados | Han transcurrido 1 h 40 min de ruta; quedan 20 minutos para la hora límite |
| **3. CONOCIMIENTO** (regla) | Regla de automatización (`services/risk.py`) | "Quedan ≤ 30 min (margen `RIESGO_MINUTOS`) y la entrega sigue activa → situación de riesgo" |
| **4. DECISIÓN** (clasificación) | El sistema clasifica | 🟡 **Entrega en riesgo** (`EN_RIESGO`, 20 min restantes) |
| **5. ACCIÓN** (salida útil) | Alerta al supervisor en el tablero + traza | ⚠️ *"La entrega #025 está cerca de su hora límite (20 min restantes)"* → el supervisor llama al repartidor y prioriza la entrega |
| **6. RETROALIMENTACIÓN** | El repartidor marca la entrega; el sistema aprende el resultado | Entregada 4:20 PM → 🔴 registrada como **retrasada (+20 min)**; alimenta el KPI `% de entregas a tiempo`, la serie diaria y el rendimiento del repartidor |

## Regla de automatización (límites definidos)

```
Para cada entrega con estado ASIGNADO o EN CAMINO:
    restante = hora_límite_del_pedido − ahora
    si restante < 0                        → 🔴 RETRASADA  (alerta RETRASO)
    si restante ≤ 30 min (configurable)    → 🟡 EN_RIESGO  (alerta RIESGO)
    en otro caso                           → 🟢 NORMAL
Entregas cerradas (ENTREGADO/CANCELADO) no se clasifican.
```

**Cuándo puede equivocarse esta regla (limitaciones):**

1. Si el repartidor **no registra su salida o su entrega a tiempo**, el estado
   almacenado está desactualizado y la clasificación puede subestimar el
   problema (dato viejo → decisión vieja).
2. No predice tráfico ni ausencia del cliente: reacciona al tiempo, no a la
   causa.
3. Si el reloj del servidor o la zona horaria (`TIME_ZONE`) están mal
   configurados, los minutos restantes se distorsionan.
4. El margen de 30 minutos es una decisión del negocio: muy grande genera
   alertas falsas, muy pequeño llega tarde.

Por eso la alerta es una **recomendación de atención**, no una decisión
automática sobre el cliente o el repartidor.

## Trazabilidad

Cada operación importante escribe una fila en `HISTORIAL_ESTADOS` con
**usuario** (o "Sistema (automatización)"), **fecha/hora**, **acción**
(estado anterior → nuevo) y **resultado** (observación, p. ej. "Entrega
completada con 20 min de retraso"). La vista *Historial* (solo administrador)
la consulta con filtros por entidad.
