from datetime import datetime
import csv
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from ventas.models import PedidoVenta, PedidoVentaItem, Cliente
from compras.models import OrdenCompra, OrdenCompraItem
from inventario.models import Producto, CategoriaProducto, Proveedor


class ReporteVentasView(LoginRequiredMixin, View):
    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        cliente_id = request.GET.get('cliente')
        producto_id = request.GET.get('producto')

        qs = PedidoVenta.objects.all().select_related('cliente')
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        if producto_id:
            qs = qs.filter(items__producto_id=producto_id).distinct()

        context = {
            'pedidos': qs.order_by('-fecha'),
            'clientes': Cliente.objects.all(),
            'productos': Producto.objects.all(),
        }
        return render(request, 'reportes/ventas.html', context)


class ReporteComprasView(LoginRequiredMixin, View):
    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        proveedor_id = request.GET.get('proveedor')
        producto_id = request.GET.get('producto')

        qs = OrdenCompra.objects.all().select_related('proveedor')
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        if proveedor_id:
            qs = qs.filter(proveedor_id=proveedor_id)
        if producto_id:
            qs = qs.filter(items__producto_id=producto_id).distinct()

        context = {
            'ordenes': qs.order_by('-fecha'),
            'proveedores': Proveedor.objects.all(),
            'productos': Producto.objects.all(),
        }
        return render(request, 'reportes/compras.html', context)


class ReporteInventarioView(LoginRequiredMixin, View):
    def get(self, request):
        categoria_id = request.GET.get('categoria')
        cantidad_min = request.GET.get('min', '')

        qs = Producto.objects.all().select_related('categoria', 'proveedor')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if cantidad_min:
            try:
                qs = qs.filter(cantidad_en_inventario__lte=int(cantidad_min))
            except ValueError:
                pass

        context = {
            'productos': qs.order_by('cantidad_en_inventario'),
            'categorias': CategoriaProducto.objects.all(),
        }
        return render(request, 'reportes/inventario.html', context)


@login_required
def reporte_ventas_csv(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    cliente_id = request.GET.get('cliente')
    producto_id = request.GET.get('producto')
    qs = PedidoVenta.objects.all().select_related('cliente')
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)
    if producto_id:
        qs = qs.filter(items__producto_id=producto_id).distinct()

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['numero', 'fecha', 'cliente', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'estado'])
    # Una fila por ítem
    items = PedidoVentaItem.objects.filter(pedido__in=qs).select_related('pedido', 'producto', 'pedido__cliente')
    if producto_id:
        items = items.filter(producto_id=producto_id)
    for it in items.order_by('-pedido__fecha', 'pedido__numero'):
        writer.writerow([
            it.pedido.numero,
            it.pedido.fecha,
            it.pedido.cliente.nombre_completo,
            it.producto.nombre,
            it.cantidad,
            it.precio_unitario,
            it.subtotal,
            it.pedido.estado,
        ])
    return response


@login_required
def reporte_compras_csv(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    proveedor_id = request.GET.get('proveedor')
    producto_id = request.GET.get('producto')
    qs = OrdenCompra.objects.all().select_related('proveedor')
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if proveedor_id:
        qs = qs.filter(proveedor_id=proveedor_id)
    if producto_id:
        qs = qs.filter(items__producto_id=producto_id).distinct()

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_compras.csv"'
    writer = csv.writer(response)
    writer.writerow(['numero', 'fecha', 'proveedor', 'producto', 'cantidad', 'costo_unitario', 'subtotal', 'estado'])
    items = OrdenCompraItem.objects.filter(orden__in=qs).select_related('orden', 'producto', 'orden__proveedor')
    if producto_id:
        items = items.filter(producto_id=producto_id)
    for it in items.order_by('-orden__fecha', 'orden__numero'):
        writer.writerow([
            it.orden.numero,
            it.orden.fecha,
            it.orden.proveedor.empresa,
            it.producto.nombre,
            it.cantidad,
            it.costo_unitario,
            it.subtotal,
            it.orden.estado,
        ])
    return response


@login_required
def reporte_inventario_csv(request):
    categoria_id = request.GET.get('categoria')
    cantidad_min = request.GET.get('min', '')
    qs = Producto.objects.all().select_related('categoria', 'proveedor')
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if cantidad_min:
        try:
            qs = qs.filter(cantidad_en_inventario__lte=int(cantidad_min))
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.csv"'
    response.write('codigo,nombre,categoria,proveedor,stock,precio_venta\n')
    for p in qs:
        response.write(f'{p.codigo},{p.nombre},{p.categoria.nombre},{p.proveedor.empresa},{p.cantidad_en_inventario},{p.precio_venta}\n')
    return response
