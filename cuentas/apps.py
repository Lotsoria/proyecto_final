"""Config de la app Cuentas.

Inicializa señales para crear grupos y asignar permisos por rol tras migraciones.
"""

from django.apps import AppConfig


class CuentasConfig(AppConfig):
    """Configuración de la aplicación de cuentas/autenticación."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'

    def ready(self):
        # Conectar señales para crear grupos y permisos
        from . import signals  # noqa: F401
