"""API JSON mínima para pruebas con Postman.

Nota: usa autenticación por sesión. Primero haz POST a /api/login para obtener
cookie de sesión y luego llama los demás endpoints. Para simplicidad MVP,
exentamos CSRF en endpoints JSON.
"""


import contextlib
import json
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from django.utils import timezone

from ventas.models import Cliente, PedidoVenta, PedidoVentaItem
from compras.models import OrdenCompra, OrdenCompraItem
from inventario.models import Producto, Proveedor, CategoriaProducto, MovimientoInventario


def _require_method(request, methods):
    return None if request.method in methods else HttpResponseNotAllowed(methods)


@csrf_exempt
def dashboard_metrics(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

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

    top_productos = list(
        PedidoVentaItem.objects.filter(pedido__estado='completado')
        .values('producto__nombre', 'producto__codigo')
        .annotate(
            unidades=Sum('cantidad'),
            monto=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )
        .order_by('-unidades')[:5]
    )

    stock_bajo = list(
        Producto.objects.filter(cantidad_en_inventario__lte=5)
        .order_by('cantidad_en_inventario')
        .values('id', 'nombre', 'cantidad_en_inventario')[:5]
    )
    stock_total = Producto.objects.aggregate(total=Sum('cantidad_en_inventario'))['total'] or 0
    compras_pendientes = OrdenCompra.objects.filter(estado='pendiente').count()

    ultimas_ventas = list(
        ventas_qs.select_related('cliente')
        .annotate(
            monto=Sum(
                F('items__cantidad') * F('items__precio_unitario'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by('-fecha')[:5]
        .values('id', 'numero', 'cliente__nombre_completo', 'fecha', 'estado', 'monto')
    )

    return JsonResponse({
        'total_hoy': str(total_hoy),
        'total_mes': str(total_mes),
        'total_completado': str(total_completado),
        'ventas_mes_count': ventas_mes.count(),
        'ventas_pendientes': ventas_pendientes,
        'compras_pendientes': compras_pendientes,
        'top_productos': top_productos,
        'stock_bajo': stock_bajo,
        'stock_total': stock_total,
        'ultimas_ventas': ultimas_ventas,
    })


@csrf_exempt
def api_login(request):
    if err := _require_method(request, ['POST']):
        return err
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    username = payload.get('username')
    password = payload.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'error': 'Credenciales inválidas'}, status=400)
    login(request, user)
    return JsonResponse({'ok': True, 'user': {'id': user.id, 'username': user.username}})


@csrf_exempt
def api_logout(request):
    if err := _require_method(request, ['POST']):
        return err
    logout(request)
    return JsonResponse({'ok': True})


def _cliente_dict(c: Cliente):
    return {
        'id': c.id,
        'nombre_completo': c.nombre_completo,
        'direccion': c.direccion,
        'telefono': c.telefono,
        'email': c.email,
    }


@csrf_exempt
def clientes_list_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        data = [_cliente_dict(c) for c in Cliente.objects.all().order_by('id')]
        return JsonResponse({'results': data})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        c = Cliente.objects.create(
            nombre_completo=payload.get('nombre_completo', ''),
            direccion=payload.get('direccion', ''),
            telefono=payload.get('telefono', ''),
            email=payload.get('email', ''),
        )
        return JsonResponse(_cliente_dict(c), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def cliente_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        c = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_cliente_dict(c))
    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        for field in ['nombre_completo', 'direccion', 'telefono', 'email']:
            if field in payload:
                setattr(c, field, payload[field])
        c.save()
        return JsonResponse(_cliente_dict(c))
    if request.method == 'DELETE':
        c.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


def _producto_dict(p: Producto):
    return {
        'id': p.id,
        'codigo': p.codigo,
        'nombre': p.nombre,
        'precio_venta': str(p.precio_venta),
        'precio_compra': str(p.precio_compra),
        'stock': p.cantidad_en_inventario,
        'proveedor': getattr(p.proveedor, 'empresa', None),
        'categoria': getattr(p.categoria, 'nombre', None),
    }


@csrf_exempt
def productos_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        data = [_producto_dict(p) for p in Producto.objects.select_related('proveedor', 'categoria').all().order_by('id')]
        return JsonResponse({'results': data})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        try:
            p = Producto.objects.create(
                codigo=payload['codigo'],
                nombre=payload['nombre'],
                descripcion=payload.get('descripcion', ''),
                precio_venta=Decimal(str(payload['precio_venta'])),
                precio_compra=Decimal(str(payload['precio_compra'])),
                cantidad_en_inventario=int(payload.get('stock', 0)),
                proveedor_id=payload['proveedor_id'],
                categoria_id=payload['categoria_id'],
                activo=bool(payload.get('activo', True)),
            )
        except KeyError as e:
            return JsonResponse({'error': f'Falta campo {e}'} , status=400)
        return JsonResponse(_producto_dict(p), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def producto_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        p = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_producto_dict(p))
    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        for field in ['codigo', 'nombre', 'descripcion']:
            if field in payload:
                setattr(p, field, payload[field])
        if 'precio_venta' in payload:
            p.precio_venta = Decimal(str(payload['precio_venta']))
        if 'precio_compra' in payload:
            p.precio_compra = Decimal(str(payload['precio_compra']))
        if 'stock' in payload:
            p.cantidad_en_inventario = int(payload['stock'])
        if 'proveedor_id' in payload:
            p.proveedor_id = payload['proveedor_id']
        if 'categoria_id' in payload:
            p.categoria_id = payload['categoria_id']
        if 'activo' in payload:
            p.activo = bool(payload['activo'])
        p.save()
        return JsonResponse(_producto_dict(p))
    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


def _proveedor_dict(p: Proveedor):
    return {
        'id': p.id,
        'empresa': p.empresa,
        'contacto_principal': p.contacto_principal,
        'telefono': p.telefono,
        'direccion': p.direccion,
    }


@csrf_exempt
def proveedores_list_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        return JsonResponse({'results': [_proveedor_dict(p) for p in Proveedor.objects.all().order_by('id')]})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        p = Proveedor.objects.create(
            empresa=payload.get('empresa', ''),
            contacto_principal=payload.get('contacto_principal', ''),
            telefono=payload.get('telefono', ''),
            direccion=payload.get('direccion', ''),
        )
        return JsonResponse(_proveedor_dict(p), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def proveedor_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        p = Proveedor.objects.get(pk=pk)
    except Proveedor.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_proveedor_dict(p))
    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        for field in ['empresa', 'contacto_principal', 'telefono', 'direccion']:
            if field in payload:
                setattr(p, field, payload[field])
        p.save()
        return JsonResponse(_proveedor_dict(p))
    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


def _categoria_dict(c: CategoriaProducto):
    return {
        'id': c.id,
        'nombre': c.nombre,
        'descripcion': c.descripcion,
    }


@csrf_exempt
def categorias_list_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        return JsonResponse({'results': [_categoria_dict(c) for c in CategoriaProducto.objects.all().order_by('id')]})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        c = CategoriaProducto.objects.create(
            nombre=payload.get('nombre', ''),
            descripcion=payload.get('descripcion', ''),
        )
        return JsonResponse(_categoria_dict(c), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def categoria_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        c = CategoriaProducto.objects.get(pk=pk)
    except CategoriaProducto.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_categoria_dict(c))
    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        for field in ['nombre', 'descripcion']:
            if field in payload:
                setattr(c, field, payload[field])
        c.save()
        return JsonResponse(_categoria_dict(c))
    if request.method == 'DELETE':
        c.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


def _venta_item_dict(it: PedidoVentaItem):
    return {
        'producto_id': it.producto_id,
        'producto': it.producto.nombre,
        'cantidad': it.cantidad,
        'precio_unitario': str(it.precio_unitario),
        'subtotal': str(it.subtotal),
    }


def _venta_dict(v: PedidoVenta):
    return {
        'id': v.id,
        'numero': v.numero,
        'fecha': str(v.fecha),
        'cliente_id': v.cliente_id,
        'cliente': v.cliente.nombre_completo,
        'estado': v.estado,
        'total': str(v.total),
        'items': [_venta_item_dict(i) for i in v.items.select_related('producto').all()],
    }


@csrf_exempt
def ventas_list_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        ventas = PedidoVenta.objects.select_related('cliente').all().order_by('-fecha', 'numero')
        return JsonResponse({'results': [_venta_dict(v) for v in ventas]})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        numero = payload.get('numero')
        cliente_id = payload.get('cliente_id')
        items = payload.get('items', [])
        if not numero or not cliente_id or not items:
            return JsonResponse({'error': 'numero, cliente_id e items son obligatorios'}, status=400)
        v = PedidoVenta.objects.create(numero=numero, cliente_id=cliente_id, estado='pendiente')
        for it in items:
            pid = it.get('producto_id')
            cant = int(it.get('cantidad', 0) or 0)
            if cant <= 0:
                return JsonResponse({'error': 'cantidad debe ser > 0'}, status=400)
            # Si no envían precio_unitario, usar precio_venta del producto
            prod = Producto.objects.get(pk=pid)
            precio = it.get('precio_unitario')
            precio = Decimal(str(precio)) if precio is not None else prod.precio_venta
            PedidoVentaItem.objects.create(pedido=v, producto_id=pid, cantidad=cant, precio_unitario=precio)
        return JsonResponse(_venta_dict(v), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def venta_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        v = PedidoVenta.objects.select_related('cliente').get(pk=pk)
    except PedidoVenta.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_venta_dict(v))
    if request.method in ('PUT', 'PATCH'):
        if v.estado != 'pendiente':
            return JsonResponse({'error': 'Solo se puede editar si está pendiente'}, status=400)
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        if 'numero' in payload:
            v.numero = payload['numero']
        if 'cliente_id' in payload:
            v.cliente_id = payload['cliente_id']
        v.save()
        if 'items' in payload:
            v.items.all().delete()
            for it in payload['items']:
                pid = it.get('producto_id')
                cant = int(it.get('cantidad', 0) or 0)
                if cant <= 0:
                    return JsonResponse({'error': 'cantidad debe ser > 0'}, status=400)
                prod = Producto.objects.get(pk=pid)
                precio = it.get('precio_unitario')
                precio = Decimal(str(precio)) if precio is not None else prod.precio_venta
                PedidoVentaItem.objects.create(pedido=v, producto_id=pid, cantidad=cant, precio_unitario=precio)
        return JsonResponse(_venta_dict(v))
    if request.method == 'DELETE':
        if v.estado != 'pendiente':
            return JsonResponse({'error': 'Solo se puede eliminar si está pendiente'}, status=400)
        v.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


@csrf_exempt
def venta_completar(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if err := _require_method(request, ['POST']):
        return err
    try:
        v = PedidoVenta.objects.get(pk=pk)
        if v.estado != 'pendiente':
            return JsonResponse({'error': 'La venta ya no está pendiente'}, status=400)
        v.estado = 'completado'
        v.save()
        return JsonResponse(_venta_dict(v))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _compra_item_dict(it: OrdenCompraItem):
    return {
        'producto_id': it.producto_id,
        'producto': it.producto.nombre,
        'cantidad': it.cantidad,
        'costo_unitario': str(it.costo_unitario),
        'subtotal': str(it.subtotal),
    }


def _compra_dict(o: OrdenCompra):
    return {
        'id': o.id,
        'numero': o.numero,
        'fecha': str(o.fecha),
        'proveedor_id': o.proveedor_id,
        'proveedor': o.proveedor.empresa,
        'estado': o.estado,
        'total': str(o.total),
        'items': [_compra_item_dict(i) for i in o.items.select_related('producto').all()],
    }


@csrf_exempt
def compras_list_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method == 'GET':
        compras = OrdenCompra.objects.select_related('proveedor').all().order_by('-fecha', 'numero')
        return JsonResponse({'results': [_compra_dict(o) for o in compras]})
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        numero = payload.get('numero')
        proveedor_id = payload.get('proveedor_id')
        items = payload.get('items', [])
        if not numero or not proveedor_id or not items:
            return JsonResponse({'error': 'numero, proveedor_id e items son obligatorios'}, status=400)
        o = OrdenCompra.objects.create(numero=numero, proveedor_id=proveedor_id, estado='pendiente')
        for it in items:
            pid = it.get('producto_id')
            cant = int(it.get('cantidad', 0) or 0)
            if cant <= 0:
                return JsonResponse({'error': 'cantidad debe ser > 0'}, status=400)
            prod = Producto.objects.get(pk=pid)
            costo = it.get('costo_unitario')
            costo = Decimal(str(costo)) if costo is not None else prod.precio_compra
            OrdenCompraItem.objects.create(orden=o, producto_id=pid, cantidad=cant, costo_unitario=costo)
        return JsonResponse(_compra_dict(o), status=201)
    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def compra_detail_update_delete(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    try:
        o = OrdenCompra.objects.select_related('proveedor').get(pk=pk)
    except OrdenCompra.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(_compra_dict(o))
    if request.method in ('PUT', 'PATCH'):
        if o.estado != 'pendiente':
            return JsonResponse({'error': 'Solo se puede editar si está pendiente'}, status=400)
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        if 'numero' in payload:
            o.numero = payload['numero']
        if 'proveedor_id' in payload:
            o.proveedor_id = payload['proveedor_id']
        o.save()
        if 'items' in payload:
            o.items.all().delete()
            for it in payload['items']:
                pid = it.get('producto_id')
                cant = int(it.get('cantidad', 0) or 0)
                if cant <= 0:
                    return JsonResponse({'error': 'cantidad debe ser > 0'}, status=400)
                prod = Producto.objects.get(pk=pid)
                costo = it.get('costo_unitario')
                costo = Decimal(str(costo)) if costo is not None else prod.precio_compra
                OrdenCompraItem.objects.create(orden=o, producto_id=pid, cantidad=cant, costo_unitario=costo)
        return JsonResponse(_compra_dict(o))
    if request.method == 'DELETE':
        if o.estado != 'pendiente':
            return JsonResponse({'error': 'Solo se puede eliminar si está pendiente'}, status=400)
        o.delete()
        return JsonResponse({}, status=204)
    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


@csrf_exempt
def compra_recibir(request, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if err := _require_method(request, ['POST']):
        return err
    try:
        o = OrdenCompra.objects.get(pk=pk)
        if o.estado != 'pendiente':
            return JsonResponse({'error': 'La orden ya no está pendiente'}, status=400)
        o.estado = 'recibida'
        o.save()
        return JsonResponse(_compra_dict(o))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def inventario_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    categoria = request.GET.get('categoria')
    minimo = request.GET.get('min')
    qs = Producto.objects.select_related('categoria', 'proveedor').all()
    if categoria:
        qs = qs.filter(categoria_id=categoria)
    if minimo:
        with contextlib.suppress(ValueError):
            qs = qs.filter(cantidad_en_inventario__lte=int(minimo))
    return JsonResponse({'results': [_producto_dict(p) for p in qs.order_by('cantidad_en_inventario')]})


def movimientos_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth requerido'}, status=401)
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    qs = MovimientoInventario.objects.select_related('producto').all()
    tipo = request.GET.get('tipo')
    pid = request.GET.get('producto')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    ref = request.GET.get('referencia')
    if tipo:
        qs = qs.filter(tipo=tipo)
    if pid:
        qs = qs.filter(producto_id=pid)
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if ref:
        qs = qs.filter(referencia__icontains=ref)
    data = [{
        'id': m.id,
        'fecha': m.fecha.isoformat(),
        'tipo': m.tipo,
        'producto_id': m.producto_id,
        'producto': m.producto.nombre,
        'cantidad': m.cantidad,
        'referencia': m.referencia,
        'nota': m.nota,
    } for m in qs.order_by('-fecha', '-id')]
    return JsonResponse({'results': data})
