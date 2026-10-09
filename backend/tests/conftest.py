"""Fixtures compartidas por las pruebas de la API."""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Repartidor, Usuario
from apps.operations.models import Entrega, Pedido

CLAVE = "Clave1234!"


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def admin(db):
    return Usuario.objects.create_user(
        "admin1", password=CLAVE, first_name="Ana", rol=Usuario.Rol.ADMIN
    )


@pytest.fixture
def repartidor(db):
    usuario = Usuario.objects.create_user(
        "carlos", password=CLAVE, first_name="Carlos", rol=Usuario.Rol.REPARTIDOR
    )
    return Repartidor.objects.create(usuario=usuario, vehiculo="Moto")


@pytest.fixture
def otro_repartidor(db):
    usuario = Usuario.objects.create_user(
        "maria", password=CLAVE, first_name="María", rol=Usuario.Rol.REPARTIDOR
    )
    return Repartidor.objects.create(usuario=usuario, vehiculo="Moto")


@pytest.fixture
def pedido(db):
    return Pedido.objects.create(
        cliente="Ferretería Demo",
        direccion="Colonia Centro, casa 12",
        hora_limite=timezone.now() + timedelta(hours=2),
    )


@pytest.fixture
def entrega(repartidor, pedido):
    return Entrega.objects.create(pedido=pedido, repartidor=repartidor)
