"""Rutas de la API JSON para pruebas con Postman.

- Autenticación de sesión: login/logout
- Clientes: listar/crear
- Productos: listar
- Ventas: listar/crear y completar
- Compras: listar/crear y recibir
- Inventario: listar con filtros
"""

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('dashboard/', views.dashboard_metrics, name='api_dashboard'),

    path('clientes/', views.clientes_list_create, name='api_clientes'),
    path('clientes/<int:pk>/', views.cliente_detail_update_delete, name='api_cliente_detail'),
    path('productos/', views.productos_list, name='api_productos'),
    path('productos/<int:pk>/', views.producto_detail_update_delete, name='api_producto_detail'),

    path('proveedores/', views.proveedores_list_create, name='api_proveedores'),
    path('proveedores/<int:pk>/', views.proveedor_detail_update_delete, name='api_proveedor_detail'),

    path('categorias/', views.categorias_list_create, name='api_categorias'),
    path('categorias/<int:pk>/', views.categoria_detail_update_delete, name='api_categoria_detail'),

    path('ventas/', views.ventas_list_create, name='api_ventas'),
    path('ventas/<int:pk>/', views.venta_detail_update_delete, name='api_venta_detail'),
    path('ventas/<int:pk>/completar/', views.venta_completar, name='api_venta_completar'),

    path('compras/', views.compras_list_create, name='api_compras'),
    path('compras/<int:pk>/', views.compra_detail_update_delete, name='api_compra_detail'),
    path('compras/<int:pk>/recibir/', views.compra_recibir, name='api_compra_recibir'),

    path('inventario/', views.inventario_list, name='api_inventario'),
    path('inventario/movimientos/', views.movimientos_list, name='api_movimientos'),
]
