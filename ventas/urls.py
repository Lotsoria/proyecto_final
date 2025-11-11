from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # Pedidos de venta (listas y detalle básico)
    path('pedidos/', views.PedidoVentaListView.as_view(), name='pedido_venta_list'),
    path('pedidos/<int:pk>/', views.PedidoVentaDetailView.as_view(), name='pedido_venta_detail'),
    path('pedidos/nuevo/', views.pedido_venta_create, name='pedido_venta_create'),
    path('pedidos/<int:pk>/editar/', views.pedido_venta_update, name='pedido_venta_update'),
    path('pedidos/<int:pk>/completar/', views.pedido_venta_completar, name='pedido_venta_complete'),
]
