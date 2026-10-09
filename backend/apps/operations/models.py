"""Modelo de datos de DeliverTrack: pedidos, entregas, incidencias,
trazabilidad (historial de estados) y alertas generadas por la automatización."""
from django.contrib.auth import get_user_model
from django.db import models

from apps.accounts.models import Repartidor

Usuario = get_user_model()


class Pedido(models.Model):
    """Pedido registrado por el administrador (fuente principal de datos)."""

    class Estado(models.TextChoices):
        RECIBIDO = "RECIBIDO", "Pedido recibido"
        PREPARANDO = "PREPARANDO", "Preparando"
        ASIGNADO = "ASIGNADO", "Asignado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    cliente = models.CharField("cliente", max_length=120)
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    direccion = models.CharField("dirección", max_length=250)
    notas = models.TextField("notas", blank=True)
    hora_limite = models.DateTimeField("hora límite de entrega")
    estado = models.CharField(
        "estado", max_length=20, choices=Estado.choices, default=Estado.RECIBIDO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido #{self.pk} · {self.cliente}"


class Entrega(models.Model):
    """Entrega: se crea cuando un pedido se asigna a un repartidor."""

    class Estado(models.TextChoices):
        ASIGNADO = "ASIGNADO", "Asignado"
        EN_CAMINO = "EN_CAMINO", "En camino"
        ENTREGADO = "ENTREGADO", "Entregado"
        INCIDENCIA = "INCIDENCIA", "Con incidencia"

    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name="entrega"
    )
    repartidor = models.ForeignKey(
        Repartidor, on_delete=models.PROTECT, related_name="entregas"
    )
    hora_asignacion = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    hora_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        "estado", max_length=20, choices=Estado.choices, default=Estado.ASIGNADO
    )

    class Meta:
        ordering = ["-hora_asignacion"]
        verbose_name = "entrega"
        verbose_name_plural = "entregas"

    def __str__(self):
        return f"Entrega #{self.pk} · pedido #{self.pedido_id}"


class Incidencia(models.Model):
    """Problema reportado por el repartidor durante una entrega."""

    class Tipo(models.TextChoices):
        CLIENTE_AUSENTE = "CLIENTE_AUSENTE", "Cliente ausente"
        DIRECCION_INCORRECTA = "DIRECCION_INCORRECTA", "Dirección incorrecta"
        VEHICULO = "VEHICULO", "Problema con el vehículo"
        TRAFICO = "TRAFICO", "Retraso por tráfico"
        OTRO = "OTRO", "Otro"

    entrega = models.ForeignKey(
        Entrega, on_delete=models.CASCADE, related_name="incidencias"
    )
    tipo = models.CharField("tipo", max_length=30, choices=Tipo.choices)
    descripcion = models.TextField("descripción")
    fecha = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField(default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "incidencia"
        verbose_name_plural = "incidencias"


class HistorialEstado(models.Model):
    """Trazabilidad de las operaciones importantes.

    Registra quién (usuario), cuándo (fecha), qué acción cambió
    (estado_anterior → estado_nuevo) y su resultado (observación).
    También deja constancia de las alertas generadas por la automatización.
    """

    class Entidad(models.TextChoices):
        PEDIDO = "PEDIDO", "Pedido"
        ENTREGA = "ENTREGA", "Entrega"

    entidad = models.CharField(max_length=10, choices=Entidad.choices)
    entidad_id = models.PositiveIntegerField()
    usuario = models.ForeignKey(
        Usuario,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acciones",
    )
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20)
    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "registro de historial"
        verbose_name_plural = "historial de estados"

    @classmethod
    def registrar(
        cls,
        *,
        entidad,
        entidad_id,
        usuario,
        estado_anterior,
        estado_nuevo,
        observacion="",
    ):
        """Punto único de escritura de la trazabilidad."""
        return cls.objects.create(
            entidad=entidad,
            entidad_id=entidad_id,
            usuario=usuario,
            estado_anterior=estado_anterior or "",
            estado_nuevo=estado_nuevo,
            observacion=observacion,
        )

    def __str__(self):
        return f"{self.entidad}#{self.entidad_id}: {self.estado_anterior or '—'} → {self.estado_nuevo}"


class Alerta(models.Model):
    """Alerta generada por la regla de automatización de riesgos."""

    class Nivel(models.TextChoices):
        RIESGO = "RIESGO", "Entrega en riesgo"
        RETRASO = "RETRASO", "Entrega retrasada"

    entrega = models.ForeignKey(
        Entrega, on_delete=models.CASCADE, related_name="alertas"
    )
    nivel = models.CharField(max_length=10, choices=Nivel.choices)
    mensaje = models.CharField(max_length=250)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "alerta"
        verbose_name_plural = "alertas"
