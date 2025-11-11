@echo off
set CONTAINER=mysql
set USER=root
set PASSWORD=Shadowdemon456.
set DATABASE=erp

docker version >nul 2>nul
if %errorlevel% neq 0 (
  echo Docker no esta disponible o no esta corriendo.
  exit /b 1
)

docker exec -i %CONTAINER% mysql -u%USER% -p%PASSWORD% -e "CREATE DATABASE IF NOT EXISTS `%DATABASE%` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
  echo No se pudo crear la base de datos en el contenedor. Verifica nombre del contenedor y credenciales.
  exit /b 1
)

echo Base de datos '%DATABASE%' creada correctamente en el contenedor '%CONTAINER%'.

