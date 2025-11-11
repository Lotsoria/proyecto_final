param(
  
  [string]$Container = "mysql",
  [string]$User = "root",
  [string]$Password = "Shadowdemon456.",
  [string]$Database = "erp"
)

$ErrorActionPreference = "Stop"

Write-Host "Creando base de datos '$Database' dentro del contenedor '$Container'..."

# Verificar que docker esté disponible
docker version *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Error "Docker no está disponible en PATH o no está corriendo."
  exit 1
}

# Crear la base de datos dentro del contenedor (pasar args explícitos)
$args = @("-u$User", "-p$Password", "-e", "CREATE DATABASE IF NOT EXISTS `$Database` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
docker exec -i $Container mysql @args | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Error "No se pudo crear la base de datos en el contenedor. Verifica nombre del contenedor y credenciales."
  exit 1
}

Write-Host "Base de datos '$Database' creada correctamente en el contenedor '$Container'."
