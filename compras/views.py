from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import OrdenCompra
from .forms import OrdenCompraForm, OrdenCompraItemFormSet
from inventario.models import Producto
import json


class OrdenCompraListView(LoginRequiredMixin, ListView):
    model = OrdenCompra
    paginate_by = 20


class OrdenCompraDetailView(LoginRequiredMixin, DetailView):
    model = OrdenCompra


@login_required
@permission_required('compras.add_ordencompra', raise_exception=True)
def orden_compra_create(request):
    orden = OrdenCompra()
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, instance=orden)
        formset = OrdenCompraItemFormSet(request.POST, instance=orden)
        if form.is_valid() and formset.is_valid():
            orden = form.save(commit=False)
            orden.estado = 'pendiente'
            orden.save()
            formset.instance = orden
            formset.save()
            messages.success(request, 'Orden de compra creada.')
            return redirect('orden_compra_detail', pk=orden.pk)
    else:
        form = OrdenCompraForm(instance=orden)
        formset = OrdenCompraItemFormSet(instance=orden)
    productos = Producto.objects.filter(activo=True).values('id', 'precio_compra')
    price_map = {str(p['id']): str(p['precio_compra']) for p in productos}
    return render(request, 'compras/ordencompra_form.html', {
        'form': form,
        'formset': formset,
        'crear': True,
        'price_map_json': json.dumps(price_map),
    })


@login_required
@permission_required('compras.change_ordencompra', raise_exception=True)
def orden_compra_update(request, pk: int):
    orden = OrdenCompra.objects.get(pk=pk)
    if orden.estado != 'pendiente':
        messages.error(request, 'Solo se pueden editar órdenes en estado pendiente.')
        return redirect('orden_compra_detail', pk=orden.pk)
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, instance=orden)
        formset = OrdenCompraItemFormSet(request.POST, instance=orden)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Orden de compra actualizada.')
            return redirect('orden_compra_detail', pk=orden.pk)
    else:
        form = OrdenCompraForm(instance=orden)
        formset = OrdenCompraItemFormSet(instance=orden)
    productos = Producto.objects.filter(activo=True).values('id', 'precio_compra')
    price_map = {str(p['id']): str(p['precio_compra']) for p in productos}
    return render(request, 'compras/ordencompra_form.html', {
        'form': form,
        'formset': formset,
        'crear': False,
        'orden': orden,
        'price_map_json': json.dumps(price_map),
    })


@login_required
@permission_required('compras.change_ordencompra', raise_exception=True)
def orden_compra_recibir(request, pk: int):
    orden = OrdenCompra.objects.get(pk=pk)
    if request.method == 'POST':
        if orden.estado != 'pendiente':
            messages.error(request, 'La orden ya no está pendiente.')
            return redirect('orden_compra_detail', pk=orden.pk)
        try:
            orden.estado = 'recibida'
            orden.save()
            messages.success(request, 'Orden recibida y stock actualizado.')
        except Exception as e:
            messages.error(request, f'No se pudo recibir: {e}')
        return redirect('orden_compra_detail', pk=orden.pk)
    return redirect('orden_compra_detail', pk=orden.pk)
"""
Vistas del módulo de compras.

- Listado y detalle de órdenes de compra (CBV)
- Crear/editar órdenes con formset de ítems
- Recibir orden (genera movimientos de inventario de entrada)

Permisos:
- Crear: compras.add_ordencompra
- Editar/Recibir: compras.change_ordencompra
"""
