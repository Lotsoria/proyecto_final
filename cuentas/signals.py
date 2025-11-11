from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Esperar hasta que existan los ContentTypes de nuestras apps (evita fallar en migración temprana)
    required_cts = [
        ('ventas', 'cliente'), ('ventas', 'pedidoventa'), ('ventas', 'pedidoventaitem'),
        ('compras', 'ordencompra'), ('compras', 'ordencompraitem'),
        ('inventario', 'producto'), ('inventario', 'categoriaproducto'), ('inventario', 'proveedor'),
    ]
    try:
        for app_label, model in required_cts:
            ContentType.objects.get_by_natural_key(app_label, model)
    except ContentType.DoesNotExist:
        # Aún no están listas todas las apps; la señal se ejecutará de nuevo después
        return

    # Crear grupos básicos
    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    vendedor_group, _ = Group.objects.get_or_create(name='Vendedor')
    comprador_group, _ = Group.objects.get_or_create(name='Comprador')

    # Helper para reunir permisos por modelo
    def perms_for(app_label, model_names, actions=('add', 'change', 'delete', 'view')):
        collected = []
        for model_name in model_names:
            try:
                ct = ContentType.objects.get_by_natural_key(app_label, model_name)
            except ContentType.DoesNotExist:
                continue
            for act in actions:
                codename = f"{act}_{model_name}"
                try:
                    collected.append(Permission.objects.get(content_type=ct, codename=codename))
                except Permission.DoesNotExist:
                    continue
        return collected

    # Administrador: todos los permisos actuales
    admin_group.permissions.set(Permission.objects.all())

    # Vendedor: ventas + inventario (ver/cambiar principales)
    ventas_models = ['cliente', 'pedidoventa', 'pedidoventaitem']
    inv_models_view_change = ['producto', 'categoriaproducto']
    vendedor_perms = perms_for('ventas', ventas_models) + perms_for('inventario', inv_models_view_change)
    vendedor_group.permissions.set(vendedor_perms)

    # Comprador: compras + inventario (ver/cambiar principales)
    compras_models = ['ordencompra', 'ordencompraitem']
    comprador_perms = perms_for('compras', compras_models) + perms_for('inventario', inv_models_view_change)
    comprador_group.permissions.set(comprador_perms)
