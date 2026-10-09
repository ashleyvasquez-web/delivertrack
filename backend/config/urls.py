"""Rutas principales de la API de DeliverTrack."""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    LoginView,
    MiPerfilView,
    RepartidorViewSet,
    UsuarioViewSet,
)
from apps.analytics import views as analitica_views
from apps.operations.views import (
    AlertaViewSet,
    EntregaViewSet,
    HistorialViewSet,
    PedidoViewSet,
)

router = DefaultRouter()
router.register("pedidos", PedidoViewSet, basename="pedidos")
router.register("entregas", EntregaViewSet, basename="entregas")
router.register("usuarios", UsuarioViewSet, basename="usuarios")
router.register("repartidores", RepartidorViewSet, basename="repartidores")
router.register("historial", HistorialViewSet, basename="historial")
router.register("alertas", AlertaViewSet, basename="alertas")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticación
    path("api/auth/token/", LoginView.as_view(), name="token_obtain_pair"),
    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("api/me/", MiPerfilView.as_view(), name="me"),
    # Recursos
    path("api/", include(router.urls)),
    # Analítica (tecnología habilitadora: analítica de datos)
    path("api/analitica/resumen/", analitica_views.resumen),
    path("api/analitica/kpis/", analitica_views.kpis),
    path("api/analitica/entregas-por-dia/", analitica_views.entregas_por_dia),
    path("api/analitica/puntualidad/", analitica_views.puntualidad),
    path("api/analitica/por-repartidor/", analitica_views.por_repartidor),
    path(
        "api/analitica/incidencias-por-tipo/",
        analitica_views.incidencias_por_tipo,
    ),
]
