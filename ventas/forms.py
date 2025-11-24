"""Formularios del módulo de ventas.

- PedidoVentaForm: datos principales del pedido
- PedidoVentaItemFormSet: ítems con validaciones (sin duplicados, cantidades/precios positivos)
"""

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import PedidoVenta, PedidoVentaItem


class PedidoVentaForm(forms.ModelForm):
    """Formulario principal del pedido de venta.

    Se capturan número y cliente. El estado se controla en la vista/modelo.
    """
    class Meta:
        model = PedidoVenta
        fields = [
            'cliente',
        ]


class BasePedidoVentaItemFormSet(BaseInlineFormSet):
    """Validaciones a nivel de formset para ítems de venta.

    - Un producto por fila (obligatorio)
    - Cantidad y precio > 0
    - No permitir productos repetidos en la misma venta
    """
    def clean(self):
        super().clean()
        productos = []
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                print('entro delete')
                continue
            producto = form.cleaned_data.get('producto')
            cantidad = form.cleaned_data.get('cantidad')
            precio = form.cleaned_data.get('precio_unitario')
            if not producto:
                raise forms.ValidationError('Debe seleccionar un producto en cada fila.')
            if not cantidad or cantidad <= 0:
                raise forms.ValidationError('La cantidad debe ser positiva.')
            if not precio or precio <= 0:
                raise forms.ValidationError('El precio unitario debe ser positivo.')
            if producto in productos:
                raise forms.ValidationError('No se puede repetir el mismo producto en la venta.')
            productos.append(producto)


PedidoVentaItemFormSet = inlineformset_factory(
    parent_model=PedidoVenta,
    model=PedidoVentaItem,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    formset=BasePedidoVentaItemFormSet,
)
