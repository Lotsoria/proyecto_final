"""Config de la app Ventas.

Registra la configuración de la app y permite enganchar señales si fuera
necesario en el futuro.
"""

from django.apps import AppConfig

class VentasConfig(AppConfig):
    """Configuración de la aplicación de ventas."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'
