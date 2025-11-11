from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import OrdenCompra


class OrdenCompraListView(LoginRequiredMixin, ListView):
    model = OrdenCompra
    paginate_by = 20


class OrdenCompraDetailView(LoginRequiredMixin, DetailView):
    model = OrdenCompra

