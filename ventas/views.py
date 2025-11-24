from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Cliente, PedidoVenta
from inventario.models import Producto
import json
from .forms import PedidoVentaForm, PedidoVentaItemFormSet


class ClienteListView(LoginRequiredMixin, ListView):
    """Lista de clientes con paginación."""
    model = Cliente
    paginate_by = 20


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Crear cliente. Requiere permiso add_cliente."""
    permission_required = 'ventas.add_cliente'
    model = Cliente
    fields = ['nombre_completo', 'direccion', 'telefono', 'email']
    success_url = reverse_lazy('cliente_list')


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar cliente. Requiere permiso change_cliente."""
    permission_required = 'ventas.change_cliente'
    model = Cliente
    fields = ['nombre_completo', 'direccion', 'telefono', 'email']
    success_url = reverse_lazy('cliente_list')


class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminar cliente. Requiere permiso delete_cliente."""
    permission_required = 'ventas.delete_cliente'
    model = Cliente
    success_url = reverse_lazy('cliente_list')


class PedidoVentaListView(LoginRequiredMixin, ListView):
    """Listado de pedidos de venta."""
    model = PedidoVenta
    paginate_by = 20


class PedidoVentaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un pedido de venta con sus ítems."""
    model = PedidoVenta


@login_required
@permission_required('ventas.add_pedidoventa', raise_exception=True)
def pedido_venta_create(request):
    """Pantalla para crear una venta con ítems.

    - Estado inicial: pendiente
    - Formset: permite múltiples productos, valida duplicados y cantidades
    - El precio se autocompleta en la UI con el precio_venta del producto
    """
    pedido = PedidoVenta()
    if request.method == 'POST':
        form = PedidoVentaForm(request.POST, instance=pedido)
        formset = PedidoVentaItemFormSet(request.POST, instance=pedido)
        if form.is_valid() and formset.is_valid():
            pedido = form.save(commit=False)
            pedido.estado = 'pendiente'
            pedido.save()
            formset.instance = pedido
            formset.save()
            messages.success(request, 'Venta creada.')
            return redirect('pedido_venta_detail', pk=pedido.pk)
    else:
        form = PedidoVentaForm(instance=pedido)
        formset = PedidoVentaItemFormSet(instance=pedido)
    productos = Producto.objects.filter(activo=True).values('id', 'precio_venta')
    price_map = {str(p['id']): str(p['precio_venta']) for p in productos}
    return render(request, 'ventas/pedidoventa_form.html', {
        'form': form,
        'formset': formset,
        'crear': True,
        'price_map_json': json.dumps(price_map),
    })


@login_required
@permission_required('ventas.change_pedidoventa', raise_exception=True)
def pedido_venta_update(request, pk: int):
    """Editar una venta pendiente.

    Solo se permite editar cuando el pedido está en estado 'pendiente'.
    """
    pedido = PedidoVenta.objects.get(pk=pk)
    if pedido.estado != 'pendiente':
        messages.error(request, 'Solo se pueden editar ventas en estado pendiente.')
        return redirect('pedido_venta_detail', pk=pedido.pk)
    if request.method == 'POST':
        form = PedidoVentaForm(request.POST, instance=pedido)
        formset = PedidoVentaItemFormSet(request.POST, instance=pedido)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Venta actualizada.')
            return redirect('pedido_venta_detail', pk=pedido.pk)
    else:
        form = PedidoVentaForm(instance=pedido)
        formset = PedidoVentaItemFormSet(instance=pedido)
    productos = Producto.objects.filter(activo=True).values('id', 'precio_venta')
    price_map = {str(p['id']): str(p['precio_venta']) for p in productos}
    return render(request, 'ventas/pedidoventa_form.html', {
        'form': form,
        'formset': formset,
        'crear': False,
        'pedido': pedido,
        'price_map_json': json.dumps(price_map),
    })


@login_required
@permission_required('ventas.change_pedidoventa', raise_exception=True)
def pedido_venta_completar(request, pk: int):
    """Marcar una venta como completada.

    - Cambia estado a 'completado'
    - La lógica del modelo crea movimientos de inventario de salida
    - Captura errores de stock insuficiente
    """
    from django.shortcuts import redirect
    pedido = PedidoVenta.objects.get(pk=pk)
    if request.method == 'POST':
        if pedido.estado != 'pendiente':
            messages.error(request, 'La venta ya no está pendiente.')
            return redirect('pedido_venta_detail', pk=pedido.pk)
        try:
            pedido.estado = 'completado'
            pedido.save()
            messages.success(request, 'Venta completada y stock actualizado.')
        except Exception as e:
            messages.error(request, f'No se pudo completar: {e}')
        return redirect('pedido_venta_detail', pk=pedido.pk)
    return redirect('pedido_venta_detail', pk=pedido.pk)
"""
Vistas del módulo de ventas.

- Listado y detalle de pedidos de venta (CBV)
- Crear/editar pedidos con formset de ítems
- Completar pedido (genera movimientos de inventario vía la lógica del modelo)

Permisos:
- Crear: ventas.add_pedidoventa
- Editar/Completar: ventas.change_pedidoventa
"""
