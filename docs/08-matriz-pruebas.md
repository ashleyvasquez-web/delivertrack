# Entregable 4 · Matriz de pruebas y evidencias

Ejecución automatizada: `cd backend && python -m pytest` — **25 pruebas, 25 superadas** (0 fallidas) en la versión entregada.

```
============================= 25 passed in 15.92s =============================
```

## 1. Matriz de pruebas automatizadas (pytest)

| ID | Requisito | Caso | Datos utilizados | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| PR-01 | RF-1 | Login válido devuelve tokens y rol | admin1 / Clave1234! | 200, `usuario.rol=ADMIN`, `access` y `refresh` | Igual | ✅ |
| PR-02 | RF-1 | Login con contraseña inválida | admin1 / incorrecta | 401 | Igual | ✅ |
| PR-03 | RF-3 | Crear pedido válido | Cliente, dirección, hora límite +3 h | 201, estado inicial RECIBIDO | Igual | ✅ |
| PR-04 | RF-3 | Hora límite en el pasado | hora límite −5 min | 400 con mensaje claro | Igual | ✅ |
| PR-05 | RF-2 | Repartidor no crea pedidos | token repartidor | 403 | Igual | ✅ |
| PR-06 | RF-2 | Anónimo no lista pedidos | sin token | 401 | Igual | ✅ |
| PR-07 | RF-4 | Preparar pedido y transición inválida | pedido RECIBIDO | 200 → PREPARANDO; repetir → 400; traza registrada | Igual | ✅ |
| PR-08 | RF-5 | Asignar entrega crea traza | pedido + repartidor | 201; pedido ASIGNADO; historial pedido+entrega | Igual | ✅ |
| PR-09 | RF-5 | Asignar dos veces el mismo pedido | mismo payload | 400 | Igual | ✅ |
| PR-10 | RF-2 | Repartidor no asigna | token repartidor | 403 | Igual | ✅ |
| PR-11 | RF-2 | Repartidor solo ve sus entregas | 2 entregas de 2 repartidores | lista filtrada; ajena → 404 | Igual | ✅ |
| PR-12 | RF-4 | Salida + entrega completas | entrega propia | EN_CAMINO → ENTREGADO; pedido ENTREGADO; 2.ª entrega → 400 | Igual | ✅ |
| PR-13 | RF-4 | Salida exige estado ASIGNADO | entrega EN_CAMINO | 400 | Igual | ✅ |
| PR-14 | RF-6 | Reportar incidencia cambia estado | CLIENTE_AUSENTE + descripción | 201; entrega INCIDENCIA | Igual | ✅ |
| PR-15 | RF-6 | Incidencia sin descripción | descripción vacía | 400 | Igual | ✅ |
| PR-16 | RF-6/RF-2 | Solo admin resuelve incidencia | repartidor → 403; admin → 200 EN_CAMINO | Igual | ✅ | ✅ |
| PR-17 | RF-7 | Entrega con tiempo suficiente | restante 2 h | NORMAL | Igual | ✅ |
| PR-18 | RF-7 | Margen de riesgo (límite de 30 min) | restante 30 y 15 min | EN_RIESGO | Igual | ✅ |
| PR-19 | RF-7 | Hora límite superada | restante −20 min | RETRASADA, minutos −20 | Igual | ✅ |
| PR-20 | RF-7 | Entrega cerrada no se clasifica | estado ENTREGADO | CERRADA | Igual | ✅ |
| PR-21 | RF-7 | Alerta sin duplicar | 2 evaluaciones seguidas | 1 alerta activa | Igual | ✅ |
| PR-22 | RF-8 | Resumen solo para admin | admin → 200; repartidor → 403 | Igual | ✅ | ✅ |
| PR-23 | RF-9 | KPIs con entrega cerrada | 1 entrega a tiempo | totales=1, a_tiempo=1, 100 %, tiempo>0 | Igual | ✅ |
| PR-24 | RF-10 | Historial registra operaciones | asignación | ≥ 2 filas con usuario, fecha, entidad | Igual | ✅ |
| PR-25 | RF-2 | Repartidor no ve historial | token repartidor | 403 | Igual | ✅ |

## 2. Pruebas de indisponibilidad / conectividad (manuales)

| ID | Caso | Procedimiento | Resultado esperado | Estado |
|---|---|---|---|---|
| PR-M1 | Backend caído | Detener Django y usar la app | Mensaje "No hay conexión con el servidor…" sin pantalla en blanco ni pérdida de sesión | ✅ Verificado en demo local |
| PR-M2 | Conexión móvil perd (repartidor) | Modo avión al marcar salida | Mensaje de error; la acción puede reintentarse al reconocer red; el estado en la base no se corrompe | ✅ Verificado en demo local |
| PR-M3 | Token expirado | Esperar expiración y operar | Renovación automática con `refresh` o redirección a login | ✅ Verificado en demo local |

## 3. Verificación de la automatización (coherencia y casos de error)

La regla puede equivocarse en estos casos (documentados y aceptados):

1. **Estado desactualizado:** si el repartidor no marcó la salida, el sistema
   puede clasificar NORMAL una entrega que en la calle ya está perdida.
2. **Hora límite mal registrada:** una hora límite irreal genera alertas
   falsas (el registro valida que sea futura, pero no que sea razonable).
3. **Margen fijo:** entregas muy lejanas (zona rural) necesitarían un margen
   mayor; por eso `RIESGO_MINUTOS` es configurable.

Cobertura de esos casos: PR-17…PR-21 verifican la coherencia de la clasificación
en los tres niveles y el caso cerrado.

## 4. Plantilla de prueba de usabilidad (3 personas)

Completar durante la práctica con usuarios representativos (1 supervisor,
2 repartidores):

| Persona | Rol representado | Tareas (login, registrar pedido, marcar salida, entregar, leer alerta) | Tiempo | Errores cometidos | Comentarios |
|---|---|---|---|---|---|
| 1 | Supervisor | — | — | — | — |
| 2 | Repartidor | — | — | — | — |
| 3 | Repartidor | — | — | — | — |
