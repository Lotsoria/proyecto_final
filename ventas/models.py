"""Modelos de ventas.

- Cliente: datos de clientes
- PedidoVenta: cabecera de venta, controla transiciones de estado
- PedidoVentaItem: detalle (producto, cantidad, precio)

Reglas de negocio principales:
- No se puede cambiar el estado una vez completado/cancelado
- Al completar una venta se crean movimientos de inventario de salida
  (esto descuenta stock mediante la lógica de MovimientoInventario)
"""

import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction

from inventario.models import Producto


class Cliente(models.Model):
    """Cliente de la empresa."""
    nombre_completo = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.nombre_completo


class PedidoVenta(models.Model):
    """Cabecera de pedido de venta.

    - estado: pendiente|completado|cancelado
    - total: calculado a partir de los ítems
    - completar(): valida stock y crea movimientos de salida
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    numero = models.CharField(max_length=30, unique=True)
    fecha = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Venta {self.numero}"

    @classmethod
    def generar_numero(cls) -> str:
        """Genera un número incremental con prefijo V-."""
        prefijo = "V-"
        with transaction.atomic():
            ultimo = cls.objects.select_for_update().order_by('-id').first()
            ultimo_num = 0
            if ultimo and ultimo.numero:
                match = re.search(r'(\d+)$', ultimo.numero)
                if match:
                    ultimo_num = int(match.group(1))
            return f"{prefijo}{ultimo_num + 1:04d}"

    @property
    def total(self) -> Decimal:
        return sum((i.subtotal for i in self.items.all()), Decimal('0.00'))

    def clean(self):
        if self.pk:
            anterior = PedidoVenta.objects.get(pk=self.pk)
            if anterior.estado in ['completado', 'cancelado'] and self.estado != anterior.estado:
                raise ValidationError('No se puede cambiar el estado una vez finalizado o cancelado')

    def completar(self):
        from inventario.models import MovimientoInventario
        # Verificar stock
        for item in self.items.all():
            if item.cantidad > item.producto.cantidad_en_inventario:
                raise ValidationError(f'Stock insuficiente para {item.producto}')
        # Crear movimientos de salida
        for item in self.items.all():
            MovimientoInventario.objects.create(
                tipo=MovimientoInventario.SALIDA,
                producto=item.producto,
                cantidad=item.cantidad,
                referencia=self.numero,
                nota='Venta completada',
                ref_venta_id=self.id,
            )

    def save(self, *args, **kwargs):
        # Al pasar a 'completado' se generan movimientos de salida.
        is_new = self.pk is None
        old_estado = None
        if is_new and not self.numero:
            with transaction.atomic():
                self.numero = self.generar_numero()
                super().save(*args, **kwargs)
            return
        if not is_new:
            old_estado = PedidoVenta.objects.get(pk=self.pk).estado
        super().save(*args, **kwargs)
        if not is_new and old_estado != self.estado and self.estado == 'completado':
            # al marcar completado, genera movimientos
            with transaction.atomic():
                self.completar()


class PedidoVentaItem(models.Model):
    """Detalle de la venta: producto, cantidad y precio unitario."""
    pedido = models.ForeignKey(PedidoVenta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self) -> Decimal:
        return (self.precio_unitario or Decimal('0.00')) * Decimal(self.cantidad or 0)

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
