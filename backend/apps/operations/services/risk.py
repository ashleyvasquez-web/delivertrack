"""Regla de automatización: clasificación de entregas activas por riesgo.

Regla de negocio (límites claramente definidos)
-----------------------------------------------
Solo se clasifican las entregas en estado ASIGNADO o EN_CAMINO
(las entregadas o canceladas quedan fuera, nivel CERRADA):

- RETRASADA (rojo):   la hora límite del pedido ya pasó y la entrega
                      sigue sin completarse.
- EN_RIESGO (amarillo): faltan RIESGO_MINUTOS (30 por defecto) minutos o
                      menos para la hora límite.
- NORMAL (verde):     queda más margen respecto a la hora límite.

Cuando una entrega activa se clasifica EN_RIESGO o RETRASADA se genera una
Alerta (sin duplicar alertas activas del mismo nivel) y se deja constancia
en el historial de estados.

Limitaciones conocidas (documentadas para la demo):
- No predice tráfico ni ausencia del cliente: depende de que el repartidor
  registre la salida y actualice el estado a tiempo.
- Si el pedido no tiene hora límite, la entrega no se clasifica (NORMAL).
- El margen de 30 minutos es una decisión del negocio, configurable con
  la variable RIESGO_MINUTOS.
"""
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from ..models import Alerta, Entrega, HistorialEstado

NORMAL = "NORMAL"
EN_RIESGO = "EN_RIESGO"
RETRASADA = "RETRASADA"
CERRADA = "CERRADA"

ESTADOS_EN_JUEGO = (Entrega.Estado.ASIGNADO, Entrega.Estado.EN_CAMINO)


@dataclass
class EvaluacionRiesgo:
    """Resultado de clasificar una entrega."""

    nivel: str  # NORMAL | EN_RIESGO | RETRASADA | CERRADA
    minutos_restantes: int | None  # negativo = minutos de retraso


def clasificar(entrega: Entrega, ahora=None) -> EvaluacionRiesgo:
    """Clasifica una entrega según el tiempo restante hasta su hora límite."""
    ahora = ahora or timezone.now()
    if entrega.estado not in ESTADOS_EN_JUEGO:
        return EvaluacionRiesgo(CERRADA, None)

    limite = entrega.pedido.hora_limite
    if limite is None:
        return EvaluacionRiesgo(NORMAL, None)

    restante = limite - ahora
    minutos = int(restante.total_seconds() // 60)
    if restante.total_seconds() < 0:
        return EvaluacionRiesgo(RETRASADA, minutos)
    if restante.total_seconds() <= settings.RIESGO_MINUTOS * 60:
        return EvaluacionRiesgo(EN_RIESGO, minutos)
    return EvaluacionRiesgo(NORMAL, minutos)


def evaluar(entrega: Entrega) -> EvaluacionRiesgo:
    """Clasifica una entrega y, si corresponde, genera una alerta sin duplicar."""
    evaluacion = clasificar(entrega)

    if evaluacion.nivel == RETRASADA:
        nivel = Alerta.Nivel.RETRASO
        mensaje = (
            f"La entrega #{entrega.pk} superó su hora límite "
            f"({abs(evaluacion.minutos_restantes)} min de retraso)."
        )
    elif evaluacion.nivel == EN_RIESGO:
        nivel = Alerta.Nivel.RIESGO
        mensaje = (
            f"La entrega #{entrega.pk} está cerca de su hora límite "
            f"({evaluacion.minutos_restantes} min restantes)."
        )
    else:
        return evaluacion

    ya_activa = Alerta.objects.filter(
        entrega=entrega, nivel=nivel, leida=False
    ).exists()
    if not ya_activa:
        Alerta.objects.create(entrega=entrega, nivel=nivel, mensaje=mensaje)
        # La automatización también deja traza (usuario nulo = sistema).
        HistorialEstado.registrar(
            entidad=HistorialEstado.Entidad.ENTREGA,
            entidad_id=entrega.pk,
            usuario=None,
            estado_anterior=entrega.estado,
            estado_nuevo=entrega.estado,
            observacion=f"Automatización: {mensaje}",
        )
    return evaluacion


def evaluar_activas():
    """Evalúa todas las entregas activas (tablero y comando programado)."""
    activas = (
        Entrega.objects.filter(estado__in=ESTADOS_EN_JUEGO)
        .select_related("pedido")
    )
    return [evaluar(entrega) for entrega in activas]
