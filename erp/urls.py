"""URL principal del proyecto.

Incluye rutas de apps:
- cuentas: login/logout y dashboard
- inventario: categorías, proveedores, productos
- ventas: clientes y pedidos de venta
- compras: órdenes de compra
- reportes: reportes HTML/CSV
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('cuentas/', include('cuentas.urls')),
    path('inventario/', include('inventario.urls')),
    path('ventas/', include('ventas.urls')),
    path('compras/', include('compras.urls')),
    path('reportes/', include('reportes.urls')),
    path('', include('cuentas.urls')),  # dashboard y login por defecto
]
