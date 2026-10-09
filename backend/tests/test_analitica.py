"""Pruebas de la analítica y de la trazabilidad visible."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.operations.models import Entrega, Pedido


@pytest.mark.django_db
def test_resumen_solo_admin(api, admin, repartidor):
    api.force_authenticate(admin)
    respuesta = api.get("/api/analitica/resumen/")
    assert respuesta.status_code == 200
    assert "en_riesgo" in respuesta.data
    assert "retrasadas" in respuesta.data

    api.force_authenticate(repartidor.usuario)
    assert api.get("/api/analitica/resumen/").status_code == 403


@pytest.mark.django_db
def test_kpis_con_entrega_cerrada(api, admin, repartidor):
    pedido = Pedido.objects.create(
        cliente="Cliente KPI",
        direccion="Dirección 1",
        hora_limite=timezone.now() + timedelta(minutes=30),
    )
    Entrega.objects.create(
        pedido=pedido,
        repartidor=repartidor,
        estado=Entrega.Estado.ENTREGADO,
        hora_salida=timezone.now() - timedelta(minutes=30),
        hora_entrega=timezone.now() - timedelta(minutes=5),
    )
    api.force_authenticate(admin)
    respuesta = api.get("/api/analitica/kpis/")
    assert respuesta.status_code == 200
    assert respuesta.data["entregas_totales"] == 1
    assert respuesta.data["a_tiempo"] == 1
    assert respuesta.data["pct_a_tiempo"] == 100.0
    assert respuesta.data["tiempo_promedio_min"] > 0


@pytest.mark.django_db
def test_historial_registra_operaciones(api, admin, repartidor, pedido):
    api.force_authenticate(admin)
    api.post(
        "/api/entregas/asignar/",
        {"pedido_id": pedido.id, "repartidor_id": repartidor.id},
        format="json",
    )
    respuesta = api.get("/api/historial/")
    assert respuesta.status_code == 200
    assert len(respuesta.data) >= 2  # pedido + entrega
    fila = respuesta.data[0]
    for campo in ("usuario_nombre", "estado_nuevo", "fecha", "entidad"):
        assert campo in fila


@pytest.mark.django_db
def test_repartidor_no_ve_historial(api, repartidor):
    api.force_authenticate(repartidor.usuario)
    assert api.get("/api/historial/").status_code == 403
