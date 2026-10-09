"""Serializadores de cuentas, autenticación y usuarios."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Repartidor, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "telefono",
            "is_active",
        ]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "La contraseña debe tener al menos 8 caracteres."
        },
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "telefono",
            "password",
        ]

    def create(self, datos_validados):
        password = datos_validados.pop("password")
        usuario = Usuario(
            username=datos_validados["username"],
            first_name=datos_validados.get("first_name", ""),
            last_name=datos_validados.get("last_name", ""),
            email=datos_validados.get("email", ""),
            rol=datos_validados.get("rol", Usuario.Rol.REPARTIDOR),
            telefono=datos_validados.get("telefono", ""),
        )
        usuario.set_password(password)
        usuario.save()
        # Todo usuario con rol REPARTIDOR obtiene su perfil operativo.
        if usuario.rol == Usuario.Rol.REPARTIDOR:
            from .models import Repartidor

            Repartidor.objects.get_or_create(usuario=usuario)
        return usuario

    def validate_rol(self, valor):
        if valor not in Usuario.Rol.values:
            raise serializers.ValidationError("El rol indicado no es válido.")
        return valor


class LoginSerializer(TokenObtainPairSerializer):
    """Devuelve los tokens JWT junto a los datos del usuario autenticado."""

    def validate(self, attrs):
        datos = super().validate(attrs)
        datos["usuario"] = UsuarioSerializer(self.user).data
        return datos


class RepartidorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Repartidor
        fields = ["id", "usuario", "vehiculo", "estado"]
