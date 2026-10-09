"""Vistas de autenticación y gestión de usuarios."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Repartidor, Usuario
from .permissions import EsAdmin
from .serializers import (
    LoginSerializer,
    RepartidorSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
)


class LoginView(TokenObtainPairView):
    """Login con usuario y contraseña; devuelve access/refresh + datos del usuario."""

    serializer_class = LoginSerializer


class MiPerfilView(APIView):
    """Devuelve los datos del usuario autenticado (el frontend lo usa al recargar)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """Gestión de usuarios del sistema (solo administrador)."""

    queryset = Usuario.objects.all().order_by("username")
    permission_classes = [EsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.query_params.get("rol")
        if rol:
            qs = qs.filter(rol=rol)
        return qs


class RepartidorViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de repartidores, usado por el administrador al asignar entregas."""

    queryset = Repartidor.objects.select_related("usuario").all()
    serializer_class = RepartidorSerializer
    permission_classes = [EsAdmin]
