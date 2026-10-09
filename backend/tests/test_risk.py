"""Pruebas de la regla de automatización (clasificación de riesgo)."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.operations.models import Alerta, Entrega, Pedido
from apps.operations.services.risk import clasificar, evaluar


@pytest.mark.django_db
def test_entrega_con_tiempo_suficiente_es_normal(entrega):
    ahora = entrega.pedido.hora_limite - timedelta(hours=2)
    assert clasificar(entrega, ahora=ahora).nivel == "NORMAL"


@pytest.mark.django_db
def test_entrega_dentro_del_margen_es_en_riesgo(entrega):
    limite = entrega.pedido.hora_limite
    # Exactamente en el margen (30 min) ya cuenta como riesgo.
    assert clasificar(entrega, ahora=limite - timedelta(minutes=30)).nivel == "EN_RIESGO"
    assert clasificar(entrega, ahora=limite - timedelta(minutes=15)).nivel == "EN_RIESGO"


@pytest.mark.django_db
def test_entrega_pasada_la_hora_limite_es_retrasada(entrega):
    ahora = entrega.pedido.hora_limite + timedelta(minutes=20)
    evaluacion = clasificar(entrega, ahora=ahora)
    assert evaluacion.nivel == "RETRASADA"
    assert evaluacion.minutos_restantes == -20


@pytest.mark.django_db
def test_entrega_entregada_no_se_clasifica(entrega):
    entrega.estado = Entrega.Estado.ENTREGADO
    entrega.hora_entrega = timezone.now()
    entrega.save()
    assert clasificar(entrega).nivel == "CERRADA"


@pytest.mark.django_db
def test_evaluar_genera_alerta_y_no_duplica(entrega):
    entrega.estado = Entrega.Estado.EN_CAMINO
    entrega.save()
    Pedido.objects.filter(pk=entrega.pedido_id).update(
        hora_limite=timezone.now() + timedelta(minutes=10)
    )
    entrega.refresh_from_db()

    evaluacion = evaluar(entrega)
    assert evaluacion.nivel == "EN_RIESGO"
    assert Alerta.objects.filter(entrega=entrega).count() == 1
    assert Alerta.objects.filter(entrega=entrega, leida=False).exists()

    # Segunda evaluación: no duplica la alerta activa del mismo nivel.
    evaluar(entrega)
    assert Alerta.objects.filter(entrega=entrega).count() == 1
