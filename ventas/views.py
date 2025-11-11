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
    model = Cliente
    paginate_by = 20


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'ventas.add_cliente'
    model = Cliente
    fields = ['nombre_completo', 'direccion', 'telefono', 'email']
    success_url = reverse_lazy('cliente_list')


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'ventas.change_cliente'
    model = Cliente
    fields = ['nombre_completo', 'direccion', 'telefono', 'email']
    success_url = reverse_lazy('cliente_list')


class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'ventas.delete_cliente'
    model = Cliente
    success_url = reverse_lazy('cliente_list')


class PedidoVentaListView(LoginRequiredMixin, ListView):
    model = PedidoVenta
    paginate_by = 20


class PedidoVentaDetailView(LoginRequiredMixin, DetailView):
    model = PedidoVenta


@login_required
@permission_required('ventas.add_pedidoventa', raise_exception=True)
def pedido_venta_create(request):
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
