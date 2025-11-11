from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/', views.OrdenCompraListView.as_view(), name='orden_compra_list'),
    path('ordenes/<int:pk>/', views.OrdenCompraDetailView.as_view(), name='orden_compra_detail'),
]

