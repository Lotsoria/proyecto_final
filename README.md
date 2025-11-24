Proyecto ERP Django (Ventas, Compras, Inventario)

## Requisitos previos
- Python 3.10+ y pip
- MySQL en localhost:3306 con una base de datos vacia (nombre por defecto: erp)
- Compiladores/headers de MySQL si usas `mysqlclient` (opcional)

## Configuracion rapida (resumen de comandos)
```bash
# Crear y activar entorno virtual
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# (Opcional) Levantar MySQL en Docker
# docker run -d --name erp-mysql -e MYSQL_ROOT_PASSWORD=tu_clave -e MYSQL_DATABASE=erp -p 3306:3306 -v erp-mysql-data:/var/lib/mysql mysql:8

# Instalar dependencias
pip install -r requirements.txt

# Ajustar credenciales de DB en erp/settings.py si no usas root

# Migraciones y superusuario
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Levantar servidor
python manage.py runserver
```

## Pasos detallados
1) Clona o copia el proyecto y entra a la carpeta del repo.
2) Crea el entorno virtual y activalo:
   - Windows: `python -m venv .venv` y `./.venv/Scripts/activate`
   - Linux/macOS: `python -m venv .venv` y `source .venv/bin/activate`
3) (Opcional) Levanta MySQL en Docker si no tienes uno corriendo:
   ```bash
   docker run -d --name erp-mysql \
     -e MYSQL_ROOT_PASSWORD=tu_clave \
     -e MYSQL_DATABASE=erp \
     -p 3306:3306 \
     -v erp-mysql-data:/var/lib/mysql \
     mysql:8
   ```
   - Si ya tienes un contenedor creado, solo inicias: `docker start erp-mysql`.
4) Instala dependencias: `pip install -r requirements.txt`.
5) Configura la base de datos MySQL (en contenedor o instancia existente):
   - Crea la BD si no existe (por defecto `erp`).
   - Ajusta usuario/contrasena/host/puerto en `erp/settings.py` dentro de `DATABASES['default']` si no coinciden con tu entorno.
   - El proyecto soporta PyMySQL por defecto (se activa si esta instalado). Si prefieres `mysqlclient`, instalalo y no necesitas PyMySQL.
6) Variables de entorno (opcionales) antes de correr el servidor:
   - `SECRET_KEY`: clave secreta para Django (si no, usa un valor de desarrollo).
   - `DEBUG`: `1` para modo desarrollo, `0` para desactivar.
   - `ALLOWED_HOSTS`: lista separada por comas (ej. `localhost,127.0.0.1`).
   - `TZ`: zona horaria (ej. `America/Mexico_City`).
7) Aplica migraciones y crea superusuario:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py createsuperuser`
8) Ejecuta el servidor de desarrollo: `python manage.py runserver` y abre `http://127.0.0.1:8000`.

## Modulos incluidos
- Inventario: Categorias, Proveedores, Productos, Movimientos.
- Ventas: Clientes, Pedidos (items), transicion a "completado" genera salidas de inventario.
- Compras: Ordenes (items), transicion a "recibida" genera entradas de inventario.
- Reportes: HTML + CSV (ventas, compras, inventario). PDF pendiente.
- Autenticacion: login/logout, grupos por defecto: Administrador, Vendedor, Comprador.

## Notas adicionales
- Para entornos productivos, agrega `collectstatic`: `python manage.py collectstatic` apuntando `STATIC_ROOT` a una ruta servida por tu web server.
- Para PDF puedes usar `xhtml2pdf` o `reportlab`.
- Para graficas se usa Chart.js via CDN en plantillas de reportes.
- Validaciones basicas incluidas; se puede ampliar con `django-filter`.
