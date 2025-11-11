from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import PedidoVenta, PedidoVentaItem


class PedidoVentaForm(forms.ModelForm):
    class Meta:
        model = PedidoVenta
        fields = [
            'numero', 'cliente',
        ]


class BasePedidoVentaItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        productos = []
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
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
