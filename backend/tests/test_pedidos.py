"""Pruebas del módulo de pedidos: validaciones, permisos y flujo de estados."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.operations.models import HistorialEstado, Pedido

CLAVE = "Clave1234!"


@pytest.mark.django_db
def test_crear_pedido_valido(api, admin):
    api.force_authenticate(admin)
    datos = {
        "cliente": "Tienda La Espiga",
        "direccion": "Colonia Centro, casa 8",
        "hora_limite": (timezone.now() + timedelta(hours=3)).isoformat(),
    }
    respuesta = api.post("/api/pedidos/", datos, format="json")
    assert respuesta.status_code == 201
    # El pedido se creó en su estado inicial RECIBIDO.
    assert Pedido.objects.get().estado == "RECIBIDO"


@pytest.mark.django_db
def test_no_permite_hora_limite_pasada(api, admin):
    api.force_authenticate(admin)
    datos = {
        "cliente": "Cliente X",
        "direccion": "Dirección Y",
        "hora_limite": (timezone.now() - timedelta(minutes=5)).isoformat(),
    }
    respuesta = api.post("/api/pedidos/", datos, format="json")
    assert respuesta.status_code == 400
    assert "hora límite" in respuesta.data["hora_limite"][0]


@pytest.mark.django_db
def test_repartidor_no_puede_crear_pedidos(api, repartidor):
    api.force_authenticate(repartidor.usuario)
    datos = {
        "cliente": "Cliente X",
        "direccion": "Dirección Y",
        "hora_limite": (timezone.now() + timedelta(hours=1)).isoformat(),
    }
    assert api.post("/api/pedidos/", datos, format="json").status_code == 403


@pytest.mark.django_db
def test_anonimo_no_puede_listar(api):
    assert api.get("/api/pedidos/").status_code == 401


@pytest.mark.django_db
def test_flujo_preparar_y_transicion_invalida(api, admin, pedido):
    api.force_authenticate(admin)
    respuesta = api.post(f"/api/pedidos/{pedido.id}/preparar/")
    assert respuesta.status_code == 200
    assert respuesta.data["estado"] == "PREPARANDO"
    # Repetir la transición ya no es válido.
    assert api.post(f"/api/pedidos/{pedido.id}/preparar/").status_code == 400
    # La operación quedó trazada (usuario, fecha, acción, resultado).
    registro = HistorialEstado.objects.filter(
        entidad="PEDIDO", entidad_id=pedido.id
    ).get()
    assert registro.usuario == admin
    assert registro.estado_nuevo == "PREPARANDO"


@pytest.mark.django_db
def test_login_jwt_devuelve_rol(api, admin):
    respuesta = api.post(
        "/api/auth/token/",
        {"username": "admin1", "password": CLAVE},
        format="json",
    )
    assert respuesta.status_code == 200
    assert respuesta.data["usuario"]["rol"] == "ADMIN"
    assert "access" in respuesta.data and "refresh" in respuesta.data


@pytest.mark.django_db
def test_login_con_contraseña_invalida(api, admin):
    respuesta = api.post(
        "/api/auth/token/",
        {"username": "admin1", "password": "incorrecta"},
        format="json",
    )
    assert respuesta.status_code == 401
