# Entregable 2f · Matriz de trazabilidad: requisitos → módulos → pruebas

| Requisito (docs/01) | Módulo / componente | Prueba automatizada (backend/tests) | Prueba manual / evidencia |
|---|---|---|---|
| RF-1 Autenticación JWT | `apps.accounts` (Login JWT) | `test_login_jwt_devuelve_rol`, `test_login_con_contraseña_invalida` | Demo paso 1 (login correcto/incorrecto) |
| RF-2 Roles con permisos | `apps.accounts.permissions.EsAdmin` + filtros por rol | `test_repartidor_no_puede_crear_pedidos`, `test_repartidor_no_puede_asignar`, `test_repartidor_solo_ve_sus_entregas`, `test_resumen_solo_admin`, `test_repartidor_no_ve_historial`, `test_resolver_incidencia_solo_admin` | Repartidor no ve tablero/analítica (redirección) |
| RF-3 Registro de pedidos | `PedidoViewSet.create` | `test_crear_pedido_valido`, `test_no_permite_hora_limite_pasada` | Formulario con validación en vivo |
| RF-4 Flujo de estados | `Pedido.preparar/cancelar`, `Entrega.salida/entregar` | `test_flujo_preparar_y_transicion_invalida`, `test_flujo_completo_salida_y_entrega`, `test_salida_requiere_entrega_asignada` | Demo pasos 2–4 |
| RF-5 Asignación de entregas | `EntregaViewSet.asignar` | `test_asignar_crea_entrega_y_traza`, `test_no_permite_asignar_dos_veces` | Demo paso 2 |
| RF-6 Incidencias | `EntregaViewSet.reportar_incidencia/resolver_incidencia` | `test_reportar_incidencia_cambia_estado`, `test_incidencia_requiere_descripcion`, `test_resolver_incidencia_solo_admin` | Reporte desde el teléfono del repartidor |
| RF-7 Automatización de riesgo | `services/risk.py` + `Alerta` | `test_entrega_con_tiempo_suficiente_es_normal`, `test_entrega_dentro_del_margen_es_en_riesgo`, `test_entrega_pasada_la_hora_limite_es_retrasada`, `test_entrega_entregada_no_se_clasifica`, `test_evaluar_genera_alerta_y_no_duplica` | Tablero muestra 🟡/🔴 y alertas; `manage.py evaluar_riesgos` |
| RF-8 Tablero | `frontend/src/pages/Dashboard.jsx` + `/api/analitica/resumen/` | `test_resumen_solo_admin` | Demo paso 1 |
| RF-9 Analítica | `apps.analytics` + Chart.js | `test_kpis_con_entrega_cerrada` | Vista Analítica con datos sintéticos |
| RF-10 Trazabilidad | `HistorialEstado.registrar` + vista Historial | `test_asignar_crea_entrega_y_traza` (filas de historial), `test_flujo_preparar_y_transicion_invalida` (usuario/fecha/acción), `test_historial_registra_operaciones` | Vista Historial con filtros |
| RNF Seguridad (secretos) | `.env.example`, `settings.py` | Revisión de configuración | Repositorio sin claves; `DEBUG=0` produce error si falta la clave |
| Indisponibilidad | Mensaje de red del frontend (`api.js`) | — | Prueba manual: detener el backend → mensaje "No hay conexión con el servidor…" sin perder sesión |
