"""Config de la app Compras."""

from django.apps import AppConfig


class ComprasConfig(AppConfig):
    """Configuración de la aplicación de compras."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compras'
