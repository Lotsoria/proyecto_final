"""Admin de Ventas.

Permite gestionar clientes y pedidos con ítems en línea.
"""

from django.contrib import admin
from .models import Cliente, PedidoVenta, PedidoVentaItem


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin de clientes."""
    list_display = ("nombre_completo", "telefono", "email")
    search_fields = ("nombre_completo", "email")


class PedidoVentaItemInline(admin.TabularInline):
    """Ítems de pedido de venta en línea."""
    model = PedidoVentaItem
    extra = 1


@admin.register(PedidoVenta)
class PedidoVentaAdmin(admin.ModelAdmin):
    """Admin de pedidos de venta con ítems inline."""
    list_display = ("numero", "fecha", "cliente", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("numero", "cliente__nombre_completo")
    inlines = [PedidoVentaItemInline]
