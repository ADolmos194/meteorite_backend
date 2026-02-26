# Script to Sync Local Database to Render Production
# Use this when you want to "push" your local modifications to the cloud

# Comando = ./sync_to_render.ps1


# 1. Variables
$LOCAL_PG_BIN = "C:\Program Files\PostgreSQL\18\bin"
$DOT_ENV = ".env"

# 2. Load Production Credentials from .env
$env_lines = Get-Content $DOT_ENV
$PROD_DB = ($env_lines | Select-String "POSTGRES_DB_PROD=").ToString().Split("=")[1].Trim()
$PROD_USER = ($env_lines | Select-String "POSTGRES_USER_PROD=").ToString().Split("=")[1].Trim()
$PROD_PASS = ($env_lines | Select-String "POSTGRES_PASSWORD_PROD=").ToString().Split("=")[1].Trim()
$PROD_HOST = ($env_lines | Select-String "POSTGRES_HOST_PROD=").ToString().Split("=")[1].Trim()
$PROD_PORT = ($env_lines | Select-String "POSTGRES_PORT_PROD=").ToString().Split("=")[1].Trim()

# 3. Local Credentials
$LOCAL_USER = ($env_lines | Select-String "POSTGRES_USER=").ToString().Split("=")[1].Trim()
$LOCAL_PASS = ($env_lines | Select-String "POSTGRES_PASSWORD=").ToString().Split("=")[1].Trim()
$LOCAL_DB = ($env_lines | Select-String "POSTGRES_DB=").ToString().Split("=")[1].Trim()
$LOCAL_PORT = ($env_lines | Select-String "POSTGRES_PORT=").ToString().Split("=")[1].Trim()

Write-Host "--- Syncing Local DB ($LOCAL_DB) to Render PROD ($PROD_DB) ---" -ForegroundColor Cyan

# 4. Generate Dump (Schema + Data)
Write-Host "Step 1: Exporting local dump..."
$env:PGPASSWORD = $LOCAL_PASS
& "$LOCAL_PG_BIN\pg_dump.exe" -h localhost -p $LOCAL_PORT -U $LOCAL_USER -d $LOCAL_DB --no-owner --no-privileges --file=sync_dump.sql

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error during export. Is the Docker container running?" -ForegroundColor Red
    exit $LASTEXITCODE
}

# 5. Push to Render
Write-Host "Step 2: Pushing to Render..."
$env:PGPASSWORD = $PROD_PASS
$RENDER_URL = "postgresql://$PROD_USER`:$PROD_PASS@$PROD_HOST`:$PROD_PORT/$PROD_DB"
& "$LOCAL_PG_BIN\psql.exe" $RENDER_URL -f sync_dump.sql

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error during import to Render." -ForegroundColor Red
} else {
    Write-Host "Sync Complete! Local changes are now in Render." -ForegroundColor Green
}

# 6. Cleanup
Remove-Item sync_dump.sql -ErrorAction SilentlyContinue
