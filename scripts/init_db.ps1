param(
  [string]$User = "root",
  [string]$Password = "Shadowdemon456.",
  [string]$Host = "localhost",
  [int]$Port = 3306
)

$ErrorActionPreference = "Stop"

Write-Host "Creando base de datos en MySQL..."

$mysqlExe = "mysql"

& $mysqlExe --version *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Error "No se encontró el cliente 'mysql' en PATH. Instala MySQL Client y vuelve a intentar."
  exit 1
}

$schemaPath = Join-Path $PSScriptRoot "..\db\create_database.mysql.sql"

& $mysqlExe -h $Host -P $Port -u $User -p$Password -e "SOURCE `"$schemaPath`";"
if ($LASTEXITCODE -ne 0) {
  Write-Error "Error al ejecutar el script SQL. Verifica credenciales y ruta."
  exit 1
}

Write-Host "Base de datos 'erp' creada. Ejecuta migraciones de Django para crear tablas."

