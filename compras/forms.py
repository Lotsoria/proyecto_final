from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import OrdenCompra, OrdenCompraItem


class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = [
            'numero', 'proveedor',
        ]


class BaseOrdenCompraItemFormSet(BaseInlineFormSet):
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
            costo = form.cleaned_data.get('costo_unitario')
            if not producto:
                raise forms.ValidationError('Debe seleccionar un producto en cada fila.')
            if not cantidad or cantidad <= 0:
                raise forms.ValidationError('La cantidad debe ser positiva.')
            if not costo or costo <= 0:
                raise forms.ValidationError('El costo unitario debe ser positivo.')
            if producto in productos:
                raise forms.ValidationError('No se puede repetir el mismo producto en la orden.')
            productos.append(producto)


OrdenCompraItemFormSet = inlineformset_factory(
    parent_model=OrdenCompra,
    model=OrdenCompraItem,
    fields=['producto', 'cantidad', 'costo_unitario'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    formset=BaseOrdenCompraItemFormSet,
)

