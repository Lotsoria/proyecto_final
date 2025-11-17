from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from django.shortcuts import render
from django.utils import timezone

from ventas.models import PedidoVenta, PedidoVentaItem
from compras.models import OrdenCompra
from inventario.models import Producto


@login_required
def dashboard(request):
    today = timezone.localdate()
    start_month = today.replace(day=1)

    ventas_qs = PedidoVenta.objects.all()
    ventas_completadas = ventas_qs.filter(estado='completado')
    ventas_pendientes = ventas_qs.filter(estado='pendiente').count()

    ventas_hoy = ventas_completadas.filter(fecha=today)
    ventas_mes = ventas_completadas.filter(fecha__gte=start_month, fecha__lte=today)

    def total_items(qs):
        return (
            PedidoVentaItem.objects.filter(pedido__in=qs)
            .aggregate(total=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=12, decimal_places=2)))
            .get('total')
            or Decimal('0.00')
        )

    total_hoy = total_items(ventas_hoy)
    total_mes = total_items(ventas_mes)
    total_completado = total_items(ventas_completadas)

    top_productos = (
        PedidoVentaItem.objects.filter(pedido__estado='completado')
        .values('producto__nombre', 'producto__codigo')
        .annotate(
            unidades=Sum('cantidad'),
            monto=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )
        .order_by('-unidades')[:5]
    )

    stock_bajo = Producto.objects.filter(cantidad_en_inventario__lte=5).order_by('cantidad_en_inventario')[:5]
    stock_total = Producto.objects.aggregate(total=Sum('cantidad_en_inventario'))['total'] or 0

    compras_pendientes = OrdenCompra.objects.filter(estado='pendiente').count()

    ultimas_ventas = (
        ventas_qs.select_related('cliente')
        .annotate(
            monto=Sum(
                F('items__cantidad') * F('items__precio_unitario'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by('-fecha')[:5]
    )

    context = {
        'total_hoy': total_hoy,
        'total_mes': total_mes,
        'total_completado': total_completado,
        'ventas_mes_count': ventas_mes.count(),
        'ventas_pendientes': ventas_pendientes,
        'compras_pendientes': compras_pendientes,
        'top_productos': top_productos,
        'stock_bajo': stock_bajo,
        'stock_total': stock_total,
        'ultimas_ventas': ultimas_ventas,
    }
    return render(request, 'dashboard.html', context)
