"""Modelos de inventario.

- CategoriaProducto, Proveedor, Producto
- MovimientoInventario: aplica entradas/salidas y ajusta stock al guardarse

Nota: el ajuste de stock ocurre solo al crear el movimiento (save nuevo).
"""

from django.core.exceptions import ValidationError
from django.db import models


class CategoriaProducto(models.Model):
    """Clasificación de productos."""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    """Proveedor de productos."""
    empresa = models.CharField(max_length=150)
    contacto_principal = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.empresa


class Producto(models.Model):
    """Producto en inventario con stock y precios de venta/compra."""
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_en_inventario = models.IntegerField(default=0)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='productos')
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, related_name='productos')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoInventario(models.Model):
    """Movimiento de inventario de entrada/salida.

    - Al crear un movimiento, se actualiza `cantidad_en_inventario`
    - Para SALIDA se valida que exista stock suficiente
    - `referencia` puede ser número de venta/compra u otro identificador
    """
    ENTRADA = 'entrada'
    SALIDA = 'salida'
    TIPOS = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    cantidad = models.PositiveIntegerField()
    referencia = models.CharField(max_length=50, blank=True)
    nota = models.CharField(max_length=255, blank=True)

    # Referencias a ventas/compras (opcionales, texto genérico en esta fase)
    ref_venta_id = models.IntegerField(null=True, blank=True)
    ref_compra_id = models.IntegerField(null=True, blank=True)

    def clean(self):
        if self.tipo == self.SALIDA and self.cantidad > self.producto.cantidad_en_inventario:
            raise ValidationError('Stock insuficiente para realizar la salida')

    def aplicar(self):
        """Aplica el efecto del movimiento sobre el stock del producto."""
        if self.tipo == self.ENTRADA:
            self.producto.cantidad_en_inventario += int(self.cantidad)
        else:
            if self.cantidad > self.producto.cantidad_en_inventario:
                raise ValidationError('Stock insuficiente para realizar la salida')
            self.producto.cantidad_en_inventario -= int(self.cantidad)
        self.producto.save(update_fields=['cantidad_en_inventario'])

    def save(self, *args, **kwargs):
        # Solo al crear el movimiento se ajusta el stock.
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # aplicar efecto sobre el stock solo al crear
            self.aplicar()

    def __str__(self):
        return f"{self.get_tipo_display()} {self.cantidad} de {self.producto}"
