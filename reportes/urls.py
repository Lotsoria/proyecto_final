from django.urls import path
from . import views

urlpatterns = [
    path('ventas/', views.ReporteVentasView.as_view(), name='reporte_ventas'),
    path('compras/', views.ReporteComprasView.as_view(), name='reporte_compras'),
    path('inventario/', views.ReporteInventarioView.as_view(), name='reporte_inventario'),
    path('ventas.csv', views.reporte_ventas_csv, name='reporte_ventas_csv'),
    path('compras.csv', views.reporte_compras_csv, name='reporte_compras_csv'),
    path('inventario.csv', views.reporte_inventario_csv, name='reporte_inventario_csv'),
]

