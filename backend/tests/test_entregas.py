"""Pruebas del flujo de entregas: asignación, estados, permisos e incidencias."""
import pytest
from django.utils import timezone

from apps.accounts.models import Repartidor, Usuario
from apps.operations.models import Entrega, Pedido


@pytest.fixture
def otra_entrega(otro_repartidor, db):
    pedido = Pedido.objects.create(
        cliente="Cliente Ajeno",
        direccion="Barrio Norte 45",
        hora_limite=timezone.now() + timezone.timedelta(hours=2),
    )
    return Entrega.objects.create(pedido=pedido, repartidor=otro_repartidor)


@pytest.mark.django_db
def test_asignar_crea_entrega_y_traza(api, admin, repartidor, pedido):
    api.force_authenticate(admin)
    respuesta = api.post(
        "/api/entregas/asignar/",
        {"pedido_id": pedido.id, "repartidor_id": repartidor.id},
        format="json",
    )
    assert respuesta.status_code == 201
    pedido.refresh_from_db()
    assert pedido.estado == "ASIGNADO"
    assert pedido.entrega.repartidor == repartidor
    assert HistorialEstadoPedido(pedido.id)
    assert HistorialEstadoEntregaCreada()


def HistorialEstadoPedido(pedido_id):
    from apps.operations.models import HistorialEstado

    assert HistorialEstado.objects.filter(
        entidad="PEDIDO", entidad_id=pedido_id
    ).exists()
    return True


def HistorialEstadoEntregaCreada():
    from apps.operations.models import HistorialEstado

    assert HistorialEstado.objects.filter(entidad="ENTREGA").exists()
    return True


@pytest.mark.django_db
def test_no_permite_asignar_dos_veces(api, admin, repartidor, pedido):
    api.force_authenticate(admin)
    datos = {"pedido_id": pedido.id, "repartidor_id": repartidor.id}
    assert api.post("/api/entregas/asignar/", datos, format="json").status_code == 201
    assert api.post("/api/entregas/asignar/", datos, format="json").status_code == 400


@pytest.mark.django_db
def test_repartidor_no_puede_asignar(api, repartidor, pedido):
    api.force_authenticate(repartidor.usuario)
    respuesta = api.post(
        "/api/entregas/asignar/",
        {"pedido_id": pedido.id, "repartidor_id": repartidor.id},
        format="json",
    )
    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_repartidor_solo_ve_sus_entregas(api, repartidor, otro_repartidor, entrega, otra_entrega):
    api.force_authenticate(otro_repartidor.usuario)
    respuesta = api.get("/api/entregas/")
    assert respuesta.status_code == 200
    ids = [fila["id"] for fila in respuesta.data]
    assert otra_entrega.id in ids
    assert entrega.id not in ids
    # No puede leer la entrega ajena.
    assert api.get(f"/api/entregas/{entrega.id}/").status_code == 404


@pytest.mark.django_db
def test_flujo_completo_salida_y_entrega(api, repartidor, entrega):
    api.force_authenticate(repartidor.usuario)
    assert api.post(f"/api/entregas/{entrega.id}/salida/").status_code == 200
    respuesta = api.post(f"/api/entregas/{entrega.id}/entregar/")
    assert respuesta.status_code == 200
    entrega.refresh_from_db()
    assert entrega.estado == "ENTREGADO"
    assert entrega.hora_entrega is not None
    entrega.pedido.refresh_from_db()
    assert entrega.pedido.estado == "ENTREGADO"
    # No se puede entregar dos veces (control de estados).
    assert api.post(f"/api/entregas/{entrega.id}/entregar/").status_code == 400


@pytest.mark.django_db
def test_salida_requiere_entrega_asignada(api, repartidor, entrega):
    api.force_authenticate(repartidor.usuario)
    entrega.estado = Entrega.Estado.EN_CAMINO
    entrega.save()
    assert api.post(f"/api/entregas/{entrega.id}/salida/").status_code == 400


@pytest.mark.django_db
def test_reportar_incidencia_cambia_estado(api, repartidor, entrega):
    api.force_authenticate(repartidor.usuario)
    api.post(f"/api/entregas/{entrega.id}/salida/")
    respuesta = api.post(
        f"/api/entregas/{entrega.id}/reportar_incidencia/",
        {"tipo": "CLIENTE_AUSENTE", "descripcion": "No hay quien reciba."},
        format="json",
    )
    assert respuesta.status_code == 201
    entrega.refresh_from_db()
    assert entrega.estado == "INCIDENCIA"


@pytest.mark.django_db
def test_incidencia_requiere_descripcion(api, repartidor, entrega):
    api.force_authenticate(repartidor.usuario)
    api.post(f"/api/entregas/{entrega.id}/salida/")
    respuesta = api.post(
        f"/api/entregas/{entrega.id}/reportar_incidencia/",
        {"tipo": "OTRO", "descripcion": "   "},
        format="json",
    )
    assert respuesta.status_code == 400


@pytest.mark.django_db
def test_resolver_incidencia_solo_admin(api, admin, repartidor, entrega):
    api.force_authenticate(repartidor.usuario)
    api.post(f"/api/entregas/{entrega.id}/salida/")
    api.post(
        f"/api/entregas/{entrega.id}/reportar_incidencia/",
        {"tipo": "DIRECCION_INCORRECTA", "descripcion": "Calle cerrada."},
        format="json",
    )
    # El repartidor no puede resolver incidencias.
    assert api.post(f"/api/entregas/{entrega.id}/resolver_incidencia/").status_code == 403
    api.force_authenticate(admin)
    respuesta = api.post(f"/api/entregas/{entrega.id}/resolver_incidencia/")
    assert respuesta.status_code == 200
    assert respuesta.data["estado"] == "EN_CAMINO"
