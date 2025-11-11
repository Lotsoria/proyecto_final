from django.contrib import admin
from .models import Cliente, PedidoVenta, PedidoVentaItem


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "telefono", "email")
    search_fields = ("nombre_completo", "email")


class PedidoVentaItemInline(admin.TabularInline):
    model = PedidoVentaItem
    extra = 1


@admin.register(PedidoVenta)
class PedidoVentaAdmin(admin.ModelAdmin):
    list_display = ("numero", "fecha", "cliente", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("numero", "cliente__nombre_completo")
    inlines = [PedidoVentaItemInline]

