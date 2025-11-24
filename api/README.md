# API JSON (ERP)

Base URL: `/api/` (autenticación por sesión). Primero inicia sesión para obtener la cookie y reutilízala en cada request.

## Autenticación
- `POST /api/login/` – body `{ "username": "", "password": "" }` → devuelve `Set-Cookie` de sesión.
- `POST /api/logout/` – cierra la sesión actual.

## Dashboard (métricas)
- `GET /api/dashboard/` – Resumen: `total_hoy`, `total_mes`, `total_completado`, `ventas_mes_count`, `ventas_pendientes`, `compras_pendientes`, `top_productos` (nombre, código, unidades, monto), `stock_bajo` (id, nombre, stock), `stock_total`, `ultimas_ventas` (id, número, cliente, fecha, estado, monto).

## Clientes
- `GET /api/clientes/` – lista.
- `POST /api/clientes/` – crea `{ nombre_completo, direccion, telefono, email }`.
- `GET /api/clientes/{id}/`
- `PUT|PATCH /api/clientes/{id}/` – actualiza campos enviados.
- `DELETE /api/clientes/{id}/`

## Proveedores
- `GET /api/proveedores/`
- `POST /api/proveedores/` – `{ empresa, contacto_principal, telefono, direccion }`
- `GET /api/proveedores/{id}/`
- `PUT|PATCH /api/proveedores/{id}/`
- `DELETE /api/proveedores/{id}/`

## Categorías
- `GET /api/categorias/`
- `POST /api/categorias/` – `{ nombre, descripcion }`
- `GET /api/categorias/{id}/`
- `PUT|PATCH /api/categorias/{id}/`
- `DELETE /api/categorias/{id}/`

## Productos
- `GET /api/productos/`
- `POST /api/productos/`
  ```json
  {
    "codigo": "SKU-001",
    "nombre": "Producto",
    "descripcion": "opcional",
    "precio_venta": 120.5,
    "precio_compra": 80.0,
    "stock": 10,
    "proveedor_id": 1,
    "categoria_id": 2,
    "activo": true
  }
  ```
- `GET /api/productos/{id}/`
- `PUT|PATCH /api/productos/{id}/` – mismos campos opcionales.
- `DELETE /api/productos/{id}/`

## Ventas
- `GET /api/ventas/` – lista con items.
- `POST /api/ventas/`
  ```json
  {
    "numero": "V-1001",
    "cliente_id": 3,
    "items": [
      { "producto_id": 5, "cantidad": 2, "precio_unitario": 120.5 }
    ]
  }
  ```
  Si no envías `precio_unitario`, usa `precio_venta` del producto.
  Si omites `numero`, se genera automáticamente con prefijo `V-`.
- `GET /api/ventas/{id}/`
- `PUT|PATCH /api/ventas/{id}/` – solo si está `pendiente`; puedes enviar `numero`, `cliente_id`, y/o `items` (se reemplazan).
- `DELETE /api/ventas/{id}/` – solo si está `pendiente`.
- `POST /api/ventas/{id}/completar/` – cambia a `completado` y descuenta inventario.

## Compras
- `GET /api/compras/`
- `POST /api/compras/`
  ```json
  {
    "numero": "OC-2001",
    "proveedor_id": 4,
    "items": [
      { "producto_id": 5, "cantidad": 10, "costo_unitario": 70.0 }
    ]
  }
  ```
- Si omites `numero`, se genera automáticamente con prefijo `OC-`.
- `GET /api/compras/{id}/`
- `PUT|PATCH /api/compras/{id}/` – solo si está `pendiente`; los `items` se reemplazan si los envías.
- `DELETE /api/compras/{id}/` – solo si está `pendiente`.
- `POST /api/compras/{id}/recibir/` – cambia a `recibida` y aumenta inventario.

## Inventario
- `GET /api/inventario/?categoria={id}&min={stock_máximo}` – lista productos; `min` filtra stock ≤ valor.
- `GET /api/inventario/movimientos/?tipo=entrada|salida&producto={id}&desde=YYYY-MM-DD&hasta=YYYY-MM-DD&referencia=texto`

## Respuestas y errores
- `401 {"error": "Auth requerido"}` si falta login.
- `400 {"error": "mensaje"}` para validaciones.
- `404 {"error": "No encontrado"}` si el recurso no existe.
- `204` sin body en deletes exitosos.

## Ejemplo rápido (cURL)
```bash
# Login y guardar cookie
curl -c cookies.txt -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pass"}'

# Crear cliente
curl -b cookies.txt -X POST http://localhost:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre_completo":"Cliente Demo","direccion":"Calle 1","telefono":"555","email":"demo@test.com"}'
```
