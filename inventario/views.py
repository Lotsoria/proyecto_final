from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import CategoriaProducto, Proveedor, Producto


class CategoriaListView(LoginRequiredMixin, ListView):
    model = CategoriaProducto
    paginate_by = 20


class CategoriaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventario.add_categoriaproducto'
    model = CategoriaProducto
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('categoria_list')


class CategoriaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventario.change_categoriaproducto'
    model = CategoriaProducto
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('categoria_list')


class CategoriaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventario.delete_categoriaproducto'
    model = CategoriaProducto
    success_url = reverse_lazy('categoria_list')


class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    paginate_by = 20


class ProveedorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventario.add_proveedor'
    model = Proveedor
    fields = ['empresa', 'contacto_principal', 'telefono', 'direccion']
    success_url = reverse_lazy('proveedor_list')


class ProveedorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventario.change_proveedor'
    model = Proveedor
    fields = ['empresa', 'contacto_principal', 'telefono', 'direccion']
    success_url = reverse_lazy('proveedor_list')


class ProveedorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventario.delete_proveedor'
    model = Proveedor
    success_url = reverse_lazy('proveedor_list')


class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    paginate_by = 20


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventario.add_producto'
    model = Producto
    fields = [
        'codigo', 'nombre', 'descripcion', 'precio_venta', 'precio_compra',
        'cantidad_en_inventario', 'proveedor', 'categoria', 'activo'
    ]
    success_url = reverse_lazy('producto_list')


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventario.change_producto'
    model = Producto
    fields = [
        'codigo', 'nombre', 'descripcion', 'precio_venta', 'precio_compra',
        'cantidad_en_inventario', 'proveedor', 'categoria', 'activo'
    ]
    success_url = reverse_lazy('producto_list')


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventario.delete_producto'
    model = Producto
    success_url = reverse_lazy('producto_list')

