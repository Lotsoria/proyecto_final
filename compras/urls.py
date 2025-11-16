"""Rutas de Compras.

- Órdenes de compra: listado, detalle, crear, editar, recibir
"""

from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/', views.OrdenCompraListView.as_view(), name='orden_compra_list'),
    path('ordenes/<int:pk>/', views.OrdenCompraDetailView.as_view(), name='orden_compra_detail'),
    path('ordenes/nueva/', views.orden_compra_create, name='orden_compra_create'),
    path('ordenes/<int:pk>/editar/', views.orden_compra_update, name='orden_compra_update'),
    path('ordenes/<int:pk>/recibir/', views.orden_compra_recibir, name='orden_compra_receive'),
]
