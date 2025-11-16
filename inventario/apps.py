"""Config de la app Inventario."""

from django.apps import AppConfig


class InventarioConfig(AppConfig):
    """Configuración de la aplicación de inventario."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
