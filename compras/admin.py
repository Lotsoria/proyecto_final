"""Admin de Compras.

Permite gestionar órdenes de compra y sus ítems.
"""

from django.contrib import admin
from .models import OrdenCompra, OrdenCompraItem


class OrdenCompraItemInline(admin.TabularInline):
    """Ítems de orden de compra en línea."""
    model = OrdenCompraItem
    extra = 1


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    """Admin de órdenes de compra con ítems inline."""
    list_display = ("numero", "fecha", "proveedor", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("numero", "proveedor__empresa")
    inlines = [OrdenCompraItemInline]
