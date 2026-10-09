from django.contrib import admin

from .models import Alerta, Entrega, HistorialEstado, Incidencia, Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "estado", "hora_limite"]
    list_filter = ["estado"]


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ["id", "pedido", "repartidor", "estado", "hora_entrega"]
    list_filter = ["estado"]


admin.site.register(Incidencia)
admin.site.register(HistorialEstado)
admin.site.register(Alerta)
