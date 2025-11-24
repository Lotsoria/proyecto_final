"""Modelos de compras.

- OrdenCompra: cabecera; al marcar como 'recibida' genera entradas de inventario
- OrdenCompraItem: detalle (producto, cantidad, costo)
"""

import re
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError

from inventario.models import Proveedor, Producto


class OrdenCompra(models.Model):
    """Cabecera de orden de compra.

    - estado: pendiente|recibida|cancelada
    - total: calculado a partir de los ítems
    - recibir(): crea movimientos de inventario de entrada
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('recibida', 'Recibida'),
        ('cancelada', 'Cancelada'),
    ]

    numero = models.CharField(max_length=30, unique=True)
    fecha = models.DateField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='ordenes')
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"OC {self.numero}"

    @classmethod
    def generar_numero(cls) -> str:
        """Genera un número incremental con prefijo OC-."""
        prefijo = "OC-"
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

    def recibir(self):
        from inventario.models import MovimientoInventario
        for item in self.items.all():
            MovimientoInventario.objects.create(
                tipo=MovimientoInventario.ENTRADA,
                producto=item.producto,
                cantidad=item.cantidad,
                referencia=self.numero,
                nota='Compra recibida',
                ref_compra_id=self.id,
            )

    def clean(self):
        if self.pk:
            anterior = OrdenCompra.objects.get(pk=self.pk)
            if anterior.estado in ['recibida', 'cancelada'] and self.estado != anterior.estado:
                raise ValidationError('No se puede cambiar el estado una vez recibida o cancelada')

    def save(self, *args, **kwargs):
        # Al pasar a 'recibida' se generan movimientos de entrada.
        is_new = self.pk is None
        old_estado = None
        if is_new and not self.numero:
            with transaction.atomic():
                self.numero = self.generar_numero()
                super().save(*args, **kwargs)
            return
        if not is_new:
            old_estado = OrdenCompra.objects.get(pk=self.pk).estado
        super().save(*args, **kwargs)
        if not is_new and old_estado != self.estado and self.estado == 'recibida':
            with transaction.atomic():
                self.recibir()


class OrdenCompraItem(models.Model):
    """Detalle de orden de compra: producto, cantidad y costo unitario."""
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self) -> Decimal:
        return (self.costo_unitario or Decimal('0.00')) * Decimal(self.cantidad or 0)

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
