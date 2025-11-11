from django.contrib import admin
from .models import CategoriaProducto, Proveedor, Producto, MovimientoInventario


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("empresa", "contacto_principal", "telefono")
    search_fields = ("empresa", "contacto_principal")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "proveedor", "precio_venta", "cantidad_en_inventario", "activo")
    list_filter = ("categoria", "proveedor", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "tipo", "producto", "cantidad", "referencia")
    list_filter = ("tipo", "fecha")
    search_fields = ("referencia", "producto__nombre", "producto__codigo")

