from django.contrib import admin
from .models import OrdenCompra, OrdenCompraItem


class OrdenCompraItemInline(admin.TabularInline):
    model = OrdenCompraItem
    extra = 1


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ("numero", "fecha", "proveedor", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("numero", "proveedor__empresa")
    inlines = [OrdenCompraItemInline]

