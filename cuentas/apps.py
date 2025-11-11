from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'

    def ready(self):
        # Conectar señales para crear grupos y permisos
        from . import signals  # noqa: F401

