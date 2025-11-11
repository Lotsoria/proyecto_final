@echo off
set USER=root
set PASSWORD=Shadowdemon456.
set HOST=localhost
set PORT=3306

where mysql >nul 2>nul
if %errorlevel% neq 0 (
  echo No se encontro el cliente "mysql" en PATH. Instala MySQL Client y reintenta.
  exit /b 1
)

set SCRIPT_DIR=%~dp0
set SCHEMA=%SCRIPT_DIR%..\db\schema.mysql.sql

mysql -h %HOST% -P %PORT% -u %USER% -p%PASSWORD% -e "SOURCE %SCHEMA%;"
if %errorlevel% neq 0 (
  echo Error al ejecutar el script SQL. Verifica credenciales y ruta.
  exit /b 1
)

echo Base de datos 'erp' creada. Ejecuta migraciones de Django para crear tablas.
