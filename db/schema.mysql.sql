-- Esquema base MySQL para el ERP (aproximado a modelos)
-- Nota: Ejecutar migraciones de Django es la fuente de verdad. Este script es de referencia.

CREATE DATABASE IF NOT EXISTS `erp` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `erp`;

-- Django creará sus tablas propias (auth, admin, etc.) mediante migraciones.
-- A continuación, tablas de dominio (simplificadas). Para llaves foráneas se asume orden de creación.

CREATE TABLE inventario_categoriaproducto (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) UNIQUE NOT NULL,
  descripcion LONGTEXT NULL
) ENGINE=InnoDB;

CREATE TABLE inventario_proveedor (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  empresa VARCHAR(150) NOT NULL,
  contacto_principal VARCHAR(100) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  direccion VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE inventario_producto (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(150) NOT NULL,
  descripcion LONGTEXT NULL,
  precio_venta DECIMAL(12,2) NOT NULL,
  precio_compra DECIMAL(12,2) NOT NULL,
  cantidad_en_inventario INT NOT NULL DEFAULT 0,
  proveedor_id BIGINT NOT NULL,
  categoria_id BIGINT NOT NULL,
  activo BOOL NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_prod_prov FOREIGN KEY (proveedor_id) REFERENCES inventario_proveedor(id),
  CONSTRAINT fk_prod_cat FOREIGN KEY (categoria_id) REFERENCES inventario_categoriaproducto(id)
) ENGINE=InnoDB;

CREATE TABLE inventario_movimientoinventario (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  fecha DATETIME(6) NOT NULL,
  tipo VARCHAR(10) NOT NULL,
  producto_id BIGINT NOT NULL,
  cantidad INT NOT NULL,
  referencia VARCHAR(50) NULL,
  nota VARCHAR(255) NULL,
  ref_venta_id INT NULL,
  ref_compra_id INT NULL,
  CONSTRAINT fk_mov_prod FOREIGN KEY (producto_id) REFERENCES inventario_producto(id)
) ENGINE=InnoDB;

CREATE TABLE ventas_cliente (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  nombre_completo VARCHAR(150) NOT NULL,
  direccion VARCHAR(255) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  email VARCHAR(254) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE ventas_pedidoventa (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  numero VARCHAR(30) NOT NULL UNIQUE,
  fecha DATE NOT NULL,
  cliente_id BIGINT NOT NULL,
  estado VARCHAR(12) NOT NULL,
  CONSTRAINT fk_pv_cliente FOREIGN KEY (cliente_id) REFERENCES ventas_cliente(id)
) ENGINE=InnoDB;

CREATE TABLE ventas_pedidoventaitem (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  pedido_id BIGINT NOT NULL,
  producto_id BIGINT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_pvi_pedido FOREIGN KEY (pedido_id) REFERENCES ventas_pedidoventa(id),
  CONSTRAINT fk_pvi_producto FOREIGN KEY (producto_id) REFERENCES inventario_producto(id)
) ENGINE=InnoDB;

CREATE TABLE compras_ordencompra (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  numero VARCHAR(30) NOT NULL UNIQUE,
  fecha DATE NOT NULL,
  proveedor_id BIGINT NOT NULL,
  estado VARCHAR(12) NOT NULL,
  CONSTRAINT fk_oc_proveedor FOREIGN KEY (proveedor_id) REFERENCES inventario_proveedor(id)
) ENGINE=InnoDB;

CREATE TABLE compras_ordencompraitem (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  orden_id BIGINT NOT NULL,
  producto_id BIGINT NOT NULL,
  cantidad INT NOT NULL,
  costo_unitario DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_oci_orden FOREIGN KEY (orden_id) REFERENCES compras_ordencompra(id),
  CONSTRAINT fk_oci_producto FOREIGN KEY (producto_id) REFERENCES inventario_producto(id)
) ENGINE=InnoDB;

-- Fin del esquema base. Ejecuta migraciones de Django para crear todo y asegurar consistencia.

