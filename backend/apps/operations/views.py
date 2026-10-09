"""Vistas de pedidos, entregas, incidencias, historial y alertas.

Organización por responsabilidad:
- PedidoViewSet: administración de pedidos (solo administrador).
- EntregaViewSet: consulta y cambio de estados (admin ve todas;
  repartidor solo las suyas, filtrando por su usuario).
- HistorialViewSet / AlertaViewSet: trazabilidad y alertas (solo admin).
"""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Repartidor
from apps.accounts.permissions import EsAdmin

from .models import Alerta, Entrega, HistorialEstado, Incidencia, Pedido
from .serializers import (
    AlertaSerializer,
    EntregaSerializer,
    HistorialSerializer,
    IncidenciaSerializer,
    PedidoCreateSerializer,
    PedidoSerializer,
)
from .services.risk import evaluar


class PedidoViewSet(viewsets.ModelViewSet):
    """Gestión de pedidos (solo administrador)."""

    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [EsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return PedidoCreateSerializer
        return PedidoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    @action(detail=True, methods=["post"])
    def preparar(self, request, pk=None):
        """RECIBIDO → PREPARANDO."""
        pedido = self.get_object()
        if pedido.estado != Pedido.Estado.RECIBIDO:
            return Response(
                {"detalle": "Solo un pedido RECIBIDO puede pasar a PREPARANDO."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pedido.estado = Pedido.Estado.PREPARANDO
        pedido.save(update_fields=["estado"])
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.PEDIDO,
            entidad_id=pedido.pk,
            usuario=request.user,
            estado_anterior=Pedido.Estado.RECIBIDO,
            estado_nuevo=Pedido.Estado.PREPARANDO,
            observacion="Pedido en preparación",
        )
        return Response(PedidoSerializer(pedido).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado in (Pedido.Estado.ENTREGADO, Pedido.Estado.CANCELADO):
            return Response(
                {"detalle": "El pedido ya no puede cancelarse."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entrega = getattr(pedido, "entrega", None)
        if entrega and entrega.estado in (
            Entrega.Estado.EN_CAMINO,
            Entrega.Estado.ENTREGADO,
        ):
            return Response(
                {"detalle": "La entrega ya salió; no se puede cancelar el pedido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        anterior = pedido.estado
        pedido.estado = Pedido.Estado.CANCELADO
        pedido.save(update_fields=["estado"])
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.PEDIDO,
            entidad_id=pedido.pk,
            usuario=request.user,
            estado_anterior=anterior,
            estado_nuevo=Pedido.Estado.CANCELADO,
            observacion="Pedido cancelado",
        )
        return Response(PedidoSerializer(pedido).data)


class EntregaViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta y cambio de estado de entregas.

    El administrador ve todas las entregas; el repartidor solo las suyas.
    Los cambios de estado validan la secuencia y dejan traza en el historial.
    """

    queryset = (
        Entrega.objects.select_related("pedido", "repartidor__usuario").all()
    )
    serializer_class = EntregaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = self.request.user
        if not usuario.es_admin:
            qs = qs.filter(repartidor__usuario=usuario)
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    @action(detail=False, methods=["post"], permission_classes=[EsAdmin])
    def asignar(self, request):
        """Crea la entrega de un pedido y la asigna a un repartidor."""
        pedido = Pedido.objects.filter(
            pk=request.data.get("pedido_id")
        ).first()
        if pedido is None:
            return Response(
                {"detalle": "El pedido indicado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pedido.estado not in (
            Pedido.Estado.RECIBIDO,
            Pedido.Estado.PREPARANDO,
        ):
            return Response(
                {
                    "detalle": f"El pedido #{pedido.pk} ya está "
                    f"«{pedido.get_estado_display()}»; no puede asignarse de nuevo."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        repartidor = Repartidor.objects.select_related("usuario").filter(
            pk=request.data.get("repartidor_id")
        ).first()
        if repartidor is None:
            return Response(
                {"detalle": "El repartidor indicado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not repartidor.usuario.is_active:
            return Response(
                {"detalle": "El repartidor está inactivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entrega = Entrega.objects.create(
            pedido=pedido,
            repartidor=repartidor,
            estado=Entrega.Estado.ASIGNADO,
        )
        anterior_pedido = pedido.estado
        pedido.estado = Pedido.Estado.ASIGNADO
        pedido.save(update_fields=["estado"])
        repartidor.estado = Repartidor.Estado.EN_RUTA
        repartidor.save(update_fields=["estado"])

        nombre = (
            repartidor.usuario.get_full_name() or repartidor.usuario.username
        )
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.PEDIDO,
            entidad_id=pedido.pk,
            usuario=request.user,
            estado_anterior=anterior_pedido,
            estado_nuevo=Pedido.Estado.ASIGNADO,
            observacion=f"Asignado a {nombre}",
        )
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=request.user,
            estado_anterior="",
            estado_nuevo=Entrega.Estado.ASIGNADO,
            observacion=f"Entrega creada y asignada a {nombre}",
        )
        evaluar(entrega)
        return Response(EntregaSerializer(entrega).data, status=201)

    @action(detail=True, methods=["post"])
    def salida(self, request, pk=None):
        """El repartidor registra que salió con la entrega (ASIGNADO → EN_CAMINO)."""
        entrega = self.get_object()
        if entrega.estado != Entrega.Estado.ASIGNADO:
            return Response(
                {"detalle": "Solo una entrega ASIGNADA puede registrar su salida."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entrega.estado = Entrega.Estado.EN_CAMINO
        entrega.hora_salida = timezone.now()
        entrega.save(update_fields=["estado", "hora_salida"])
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=request.user,
            estado_anterior=Entrega.Estado.ASIGNADO,
            estado_nuevo=Entrega.Estado.EN_CAMINO,
            observacion="Salida registrada por el repartidor",
        )
        evaluar(entrega)
        return Response(EntregaSerializer(entrega).data)

    @action(detail=True, methods=["post"])
    def entregar(self, request, pk=None):
        """Marca la entrega como completada (EN_CAMINO/INCIDENCIA → ENTREGADO)."""
        entrega = self.get_object()
        if entrega.estado not in (
            Entrega.Estado.EN_CAMINO,
            Entrega.Estado.INCIDENCIA,
        ):
            return Response(
                {
                    "detalle": "Solo una entrega EN CAMINO (o con incidencia "
                    "atendida) puede marcarse como entregada."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        anterior_entrega = entrega.estado
        entrega.estado = Entrega.Estado.ENTREGADO
        entrega.hora_entrega = timezone.now()
        entrega.save(update_fields=["estado", "hora_entrega"])

        pedido = entrega.pedido
        pedido.estado = Pedido.Estado.ENTREGADO
        pedido.save(update_fields=["estado"])

        # Las alertas de esta entrega ya no requieren atención.
        Alerta.objects.filter(entrega=entrega, leida=False).update(leida=True)

        retraso_min = int(
            (entrega.hora_entrega - pedido.hora_limite).total_seconds() // 60
        )
        observacion = "Entrega completada a tiempo"
        if retraso_min > 0:
            observacion = f"Entrega completada con {retraso_min} min de retraso"
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=request.user,
            estado_anterior=anterior_entrega,
            estado_nuevo=Entrega.Estado.ENTREGADO,
            observacion=observacion,
        )
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.PEDIDO,
            entidad_id=pedido.pk,
            usuario=request.user,
            estado_anterior=Pedido.Estado.ASIGNADO,
            estado_nuevo=Pedido.Estado.ENTREGADO,
            observacion=observacion,
        )
        return Response(EntregaSerializer(entrega).data)

    @action(detail=True, methods=["post"])
    def reportar_incidencia(self, request, pk=None):
        """El repartidor reporta un problema (→ INCIDENCIA)."""
        entrega = self.get_object()
        if entrega.estado not in (
            Entrega.Estado.ASIGNADO,
            Entrega.Estado.EN_CAMINO,
        ):
            return Response(
                {"detalle": "Solo una entrega activa puede reportar incidencia."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = IncidenciaSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(entrega=entrega)

        entrega.estado = Entrega.Estado.INCIDENCIA
        entrega.save(update_fields=["estado"])
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=request.user,
            estado_anterior=Entrega.Estado.EN_CAMINO,
            estado_nuevo=Entrega.Estado.INCIDENCIA,
            observacion=(
                f"Incidencia reportada: {serializer.validated_data['tipo']} — "
                f"{serializer.validated_data['descripcion']}"
            ),
        )
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"], permission_classes=[EsAdmin])
    def resolver_incidencia(self, request, pk=None):
        """El administrador da por atendida la incidencia (→ EN_CAMINO)."""
        entrega = self.get_object()
        incidencia = entrega.incidencias.filter(resuelta=False).first()
        if entrega.estado != Entrega.Estado.INCIDENCIA or incidencia is None:
            return Response(
                {"detalle": "La entrega no tiene una incidencia activa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        incidencia.resuelta = True
        incidencia.fecha_resolucion = timezone.now()
        incidencia.save(update_fields=["resuelta", "fecha_resolucion"])

        entrega.estado = Entrega.Estado.EN_CAMINO
        entrega.save(update_fields=["estado"])
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=request.user,
            estado_anterior=Entrega.Estado.INCIDENCIA,
            estado_nuevo=Entrega.Estado.EN_CAMINO,
            observacion=f"Incidencia resuelta: {incidencia.get_tipo_display()}",
        )
        return Response(EntregaSerializer(entrega).data)


class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    """Trazabilidad de operaciones (solo administrador)."""

    queryset = HistorialEstado.objects.select_related("usuario").all()
    serializer_class = HistorialSerializer
    permission_classes = [EsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        entidad = self.request.query_params.get("entidad")
        entidad_id = self.request.query_params.get("entidad_id")
        if entidad:
            qs = qs.filter(entidad=entidad)
        if entidad_id:
            qs = qs.filter(entidad_id=entidad_id)
        return qs


class AlertaViewSet(viewsets.ReadOnlyModelViewSet):
    """Alertas generadas por la automatización (solo administrador)."""

    queryset = Alerta.objects.select_related("entrega__pedido").all()
    serializer_class = AlertaSerializer
    permission_classes = [EsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        leida = self.request.query_params.get("leida")
        if leida in ("true", "false"):
            qs = qs.filter(leida=(leida == "true"))
        return qs

    @action(detail=True, methods=["post"])
    def leer(self, request, pk=None):
        alerta = self.get_object()
        alerta.leida = True
        alerta.save(update_fields=["leida"])
        return Response(AlertaSerializer(alerta).data)
