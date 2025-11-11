Proyecto ERP Django (Ventas, Compras, Inventario)

Pasos rápidos:

1) Variables de entorno (MySQL):

   - Establece `DATABASE_URL` (ejemplo):

     `DATABASE_URL=mysql://root:password@localhost:3306/erp`

   - Requiere driver MySQL para Django:
     - Opción A: `mysqlclient`
     - Opción B: `PyMySQL` (añadir `pymysql.install_as_MySQLdb()` en `manage.py` si lo prefieres)

2) Migraciones e inicio:

   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py createsuperuser`
   - `python manage.py runserver`

3) Módulos incluidos:

   - Inventario: Categorías, Proveedores, Productos, Movimientos.
   - Ventas: Clientes, Pedidos (ítems), transición a "completado" genera salidas de inventario.
   - Compras: Órdenes (ítems), transición a "recibida" genera entradas de inventario.
   - Reportes: HTML + CSV (ventas, compras, inventario). PDF pendiente.
   - Autenticación: login/logout, grupos por defecto: Administrador, Vendedor, Comprador.

4) Permisos y roles:
   - Se crean en `post_migrate` (ver `cuentas/signals.py`).
   - Admin tiene todos; Vendedor (ventas + ver/editar inventario básico); Comprador (compras + ver/editar inventario básico).

5) Estructura de URLs (principales):
   - `/cuentas/login`, `/cuentas/logout`, `/` (dashboard)
   - `/inventario/categorias|proveedores|productos`
   - `/ventas/clientes`, `/ventas/pedidos`
   - `/compras/ordenes`
   - `/reportes/ventas|compras|inventario` y sus `.csv`

6) Notas:
   - Para PDF, sugerido: `xhtml2pdf` o `reportlab`.
   - Para gráficas: Chart.js vía CDN en las plantillas de reportes.
   - Validaciones básicas incluidas; se puede ampliar con `django-filter`.

