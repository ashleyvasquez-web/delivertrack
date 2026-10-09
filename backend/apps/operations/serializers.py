"""Serializadores de pedidos, entregas, incidencias, historial y alertas."""
from django.utils import timezone
from rest_framework import serializers

from .models import Alerta, Entrega, HistorialEstado, Incidencia, Pedido
from .services.risk import clasificar


class PedidoResumenSerializer(serializers.ModelSerializer):
    """Datos del pedido que el repartidor necesita para la entrega."""

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "telefono",
            "direccion",
            "notas",
            "hora_limite",
            "estado",
        ]


class EntregaSerializer(serializers.ModelSerializer):
    pedido = PedidoResumenSerializer(read_only=True)
    repartidor_nombre = serializers.SerializerMethodField()
    riesgo = serializers.SerializerMethodField()
    minutos_restantes = serializers.SerializerMethodField()

    class Meta:
        model = Entrega
        fields = [
            "id",
            "pedido",
            "repartidor",
            "repartidor_nombre",
            "estado",
            "hora_asignacion",
            "hora_salida",
            "hora_entrega",
            "riesgo",
            "minutos_restantes",
        ]

    def get_repartidor_nombre(self, obj):
        usuario = obj.repartidor.usuario
        nombre = f"{usuario.first_name} {usuario.last_name}".strip()
        return nombre or usuario.username

    def get_riesgo(self, obj):
        return clasificar(obj).nivel

    def get_minutos_restantes(self, obj):
        return clasificar(obj).minutos_restantes


class PedidoSerializer(serializers.ModelSerializer):
    entrega = EntregaSerializer(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "telefono",
            "direccion",
            "notas",
            "hora_limite",
            "estado",
            "fecha_registro",
            "entrega",
        ]


class PedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ["cliente", "telefono", "direccion", "notas", "hora_limite"]

    def validate_cliente(self, valor):
        if not valor.strip():
            raise serializers.ValidationError("El nombre del cliente es obligatorio.")
        return valor.strip()

    def validate_direccion(self, valor):
        if not valor.strip():
            raise serializers.ValidationError("La dirección es obligatoria.")
        return valor.strip()

    def validate_hora_limite(self, valor):
        if valor <= timezone.now():
            raise serializers.ValidationError(
                "La hora límite debe ser posterior a la hora actual."
            )
        return valor


class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidencia
        fields = [
            "id",
            "entrega",
            "tipo",
            "descripcion",
            "fecha",
            "resuelta",
            "fecha_resolucion",
        ]
        read_only_fields = ["entrega", "resuelta", "fecha_resolucion"]

    def validate_tipo(self, valor):
        if valor not in Incidencia.Tipo.values:
            raise serializers.ValidationError("El tipo de incidencia no es válido.")
        return valor

    def validate_descripcion(self, valor):
        if not valor.strip():
            raise serializers.ValidationError(
                "La descripción del problema es obligatoria."
            )
        return valor.strip()


class HistorialSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialEstado
        fields = [
            "id",
            "entidad",
            "entidad_id",
            "usuario",
            "usuario_nombre",
            "estado_anterior",
            "estado_nuevo",
            "observacion",
            "fecha",
        ]

    def get_usuario_nombre(self, obj):
        if obj.usuario is None:
            return "Sistema (automatización)"
        nombre = f"{obj.usuario.first_name} {obj.usuario.last_name}".strip()
        return nombre or obj.usuario.username


class AlertaSerializer(serializers.ModelSerializer):
    entrega_estado = serializers.CharField(
        source="entrega.estado", read_only=True
    )
    pedido_id = serializers.IntegerField(
        source="entrega.pedido_id", read_only=True
    )

    class Meta:
        model = Alerta
        fields = [
            "id",
            "entrega",
            "pedido_id",
            "entrega_estado",
            "nivel",
            "mensaje",
            "fecha",
            "leida",
        ]
