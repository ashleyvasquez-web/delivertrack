"""Analítica de datos para la toma de decisiones (tecnología habilitadora).

Endpoints de solo lectura para el tablero del administrador:
- resumen: contadores del día y entregas en riesgo/retrasadas.
- kpis: indicadores comparables con la línea base del diagnóstico.
- entregas-por-dia: serie de los últimos 14 días.
- puntualidad, por-repartidor, incidencias-por-tipo: agregados para gráficas.

Si la variable EVALUAR_RIESGO_AL_CONSULTAR=1 (por defecto en desarrollo),
cada consulta al resumen dispara la evaluación de riesgos; en producción
el planificador (cron) ejecuta `manage.py evaluar_riesgos` cada minuto.
"""
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.models import Repartidor
from apps.accounts.permissions import EsAdmin
from apps.operations.models import Alerta, Entrega, Incidencia, Pedido
from apps.operations.services.risk import clasificar, evaluar_activas

DIAS_SERIE = 14


def _nombre_repartidor(repartidor):
    usuario = repartidor.usuario
    nombre = f"{usuario.first_name} {usuario.last_name}".strip()
    return nombre or usuario.username


def _es_a_tiempo(entrega):
    return entrega.hora_entrega <= entrega.pedido.hora_limite


@api_view(["GET"])
@permission_classes([EsAdmin])
def resumen(request):
    """Contadores del tablero principal."""
    if settings.EVALUAR_RIESGO_AL_CONSULTAR:
        evaluar_activas()

    pedidos_por_estado = dict(
        Pedido.objects.values_list("estado")
        .annotate(total=Count("id"))
        .values_list("estado", "total")
    )
    activas = Entrega.objects.filter(
        estado__in=(Entrega.Estado.ASIGNADO, Entrega.Estado.EN_CAMINO)
    ).select_related("pedido")

    en_riesgo = 0
    retrasadas = 0
    for entrega in activas:
        nivel = clasificar(entrega).nivel
        if nivel == "EN_RIESGO":
            en_riesgo += 1
        elif nivel == "RETRASADA":
            retrasadas += 1

    hoy = timezone.localdate()
    entregadas_hoy = Entrega.objects.filter(
        estado=Entrega.Estado.ENTREGADO, hora_entrega__date=hoy
    ).count()

    return Response(
        {
            "pedidos_por_estado": pedidos_por_estado,
            "pendientes": (
                pedidos_por_estado.get(Pedido.Estado.RECIBIDO, 0)
                + pedidos_por_estado.get(Pedido.Estado.PREPARANDO, 0)
            ),
            "entregas_activas": activas.count(),
            "en_camino": activas.filter(estado=Entrega.Estado.EN_CAMINO).count(),
            "entregadas_hoy": entregadas_hoy,
            "en_riesgo": en_riesgo,
            "retrasadas": retrasadas,
            "alertas_activas": Alerta.objects.filter(leida=False).count(),
            "incidencias_activas": Incidencia.objects.filter(resuelta=False).count(),
        }
    )


@api_view(["GET"])
@permission_classes([EsAdmin])
def kpis(request):
    """Indicadores clave del proceso, comparables con la línea base."""
    cerradas = (
        Entrega.objects.filter(estado=Entrega.Estado.ENTREGADO)
        .exclude(hora_entrega=None)
        .select_related("pedido")
    )
    total = cerradas.count()
    a_tiempo = 0
    duraciones = []
    for entrega in cerradas:
        inicio = entrega.hora_salida or entrega.hora_asignacion
        duraciones.append((entrega.hora_entrega - inicio).total_seconds() / 60)
        if _es_a_tiempo(entrega):
            a_tiempo += 1

    return Response(
        {
            "entregas_totales": total,
            "a_tiempo": a_tiempo,
            "retrasos": total - a_tiempo,
            "pct_a_tiempo": round(100 * a_tiempo / total, 1) if total else None,
            "tiempo_promedio_min": (
                round(sum(duraciones) / len(duraciones), 1) if duraciones else None
            ),
            "incidencias_total": Incidencia.objects.count(),
        }
    )


@api_view(["GET"])
@permission_classes([EsAdmin])
def entregas_por_dia(request):
    """Serie diaria de entregas completadas y con retraso (últimos 14 días)."""
    hoy = timezone.localdate()
    inicio = hoy - timedelta(days=DIAS_SERIE - 1)
    filas = (
        Entrega.objects.filter(
            estado=Entrega.Estado.ENTREGADO, hora_entrega__date__gte=inicio
        )
        .annotate(
            dia=TruncDate("hora_entrega", tzinfo=timezone.get_current_timezone())
        )
        .values("dia")
        .annotate(
            entregadas=Count("id"),
            retrasadas=Count(
                "id",
                filter=Q(hora_entrega__gt=F("pedido__hora_limite")),
            ),
        )
        .order_by("dia")
    )
    por_dia = {fila["dia"]: fila for fila in filas}
    serie = []
    for desplazamiento in range(DIAS_SERIE):
        dia = inicio + timedelta(days=desplazamiento)
        fila = por_dia.get(dia)
        serie.append(
            {
                "dia": dia.isoformat(),
                "entregadas": fila["entregadas"] if fila else 0,
                "retrasadas": fila["retrasadas"] if fila else 0,
            }
        )
    return Response(serie)


@api_view(["GET"])
@permission_classes([EsAdmin])
def puntualidad(request):
    """Comparación entregas a tiempo vs retrasadas (para gráfica de anillo)."""
    cerradas = (
        Entrega.objects.filter(estado=Entrega.Estado.ENTREGADO)
        .exclude(hora_entrega=None)
        .select_related("pedido")
    )
    a_tiempo = sum(1 for e in cerradas if _es_a_tiempo(e))
    total = cerradas.count()
    return Response(
        {"a_tiempo": a_tiempo, "retrasadas": total - a_tiempo, "total": total}
    )


@api_view(["GET"])
@permission_classes([EsAdmin])
def por_repartidor(request):
    """Rendimiento por repartidor: entregadas, a tiempo y % de puntualidad."""
    datos = []
    for repartidor in Repartidor.objects.select_related("usuario"):
        cerradas = repartidor.entregas.filter(
            estado=Entrega.Estado.ENTREGADO
        ).exclude(hora_entrega=None).select_related("pedido")
        total = cerradas.count()
        a_tiempo = sum(1 for e in cerradas if _es_a_tiempo(e))
        datos.append(
            {
                "repartidor": _nombre_repartidor(repartidor),
                "entregadas": total,
                "a_tiempo": a_tiempo,
                "retrasadas": total - a_tiempo,
                "pct_puntualidad": (
                    round(100 * a_tiempo / total, 1) if total else None
                ),
            }
        )
    return Response(datos)


@api_view(["GET"])
@permission_classes([EsAdmin])
def incidencias_por_tipo(request):
    """Principales causas de incidencias (para gráfica circular)."""
    filas = Incidencia.objects.values("tipo").annotate(total=Count("id")).order_by("-total")
    etiquetas = dict(Incidencia.Tipo.choices)
    return Response(
        [
            {"tipo": fila["tipo"], "etiqueta": etiquetas.get(fila["tipo"], fila["tipo"]), "total": fila["total"]}
            for fila in filas
        ]
    )
