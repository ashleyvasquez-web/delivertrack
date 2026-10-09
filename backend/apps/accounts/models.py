"""Modelos de usuarios y roles del sistema."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario de la aplicación con rol: ADMIN o REPARTIDOR."""

    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        REPARTIDOR = "REPARTIDOR", "Repartidor"

    rol = models.CharField(
        "rol", max_length=20, choices=Rol.choices, default=Rol.REPARTIDOR
    )
    telefono = models.CharField("teléfono", max_length=30, blank=True)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    @property
    def es_admin(self) -> bool:
        return self.rol == self.Rol.ADMIN


class Repartidor(models.Model):
    """Perfil operativo de un usuario repartidor."""

    class Estado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        EN_RUTA = "EN_RUTA", "En ruta"
        INACTIVO = "INACTIVO", "Inactivo"

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="repartidor"
    )
    vehiculo = models.CharField("vehículo", max_length=60, blank=True)
    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )

    class Meta:
        verbose_name = "repartidor"
        verbose_name_plural = "repartidores"

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f"Repartidor: {nombre}"
