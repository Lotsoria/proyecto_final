"""Admin de Inventario.

Registra modelos para gestión rápida desde el panel de administración.
"""

from django.contrib import admin
from .models import CategoriaProducto, Proveedor, Producto, MovimientoInventario


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    """Admin de categorías."""
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Admin de proveedores."""
    list_display = ("empresa", "contacto_principal", "telefono")
    search_fields = ("empresa", "contacto_principal")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin de productos con filtros por categoría/proveedor."""
    list_display = ("codigo", "nombre", "categoria", "proveedor", "precio_venta", "cantidad_en_inventario", "activo")
    list_filter = ("categoria", "proveedor", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """Admin de movimientos para auditoría de entradas/salidas."""
    list_display = ("fecha", "tipo", "producto", "cantidad", "referencia")
    list_filter = ("tipo", "fecha")
    search_fields = ("referencia", "producto__nombre", "producto__codigo")
