from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Repartidor, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["username", "first_name", "last_name", "rol", "is_active"]
    list_filter = ["rol", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("DeliverTrack", {"fields": ("rol", "telefono")}),
    )


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ["usuario", "vehiculo", "estado"]
    list_filter = ["estado"]
