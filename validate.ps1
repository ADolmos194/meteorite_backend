# Replicate the logic from the Makefile's "ci" target for PowerShell.

Write-Host "Starting Backend Validation..." -ForegroundColor Cyan

# 1. Build the base image
docker-compose build

# 2. Ensure the database is up
docker-compose up -d db

# 3. Run Tests
Write-Host "Running Tests..." -ForegroundColor Yellow
docker-compose run --rm web python manage.py test

# 4. Run Lint (Flake8)
Write-Host "Running Flake8..." -ForegroundColor Yellow
docker-compose run --rm web flake8 . --exclude=venv,*/migrations/*

# 5. Run Dead Code Analysis (Vulture)
Write-Host "Running Vulture..." -ForegroundColor Yellow
docker-compose run --rm web vulture . --min-confidence 80 --exclude venv,*/migrations/*

# 6. Run Security Audit (Bandit)
Write-Host "Running Bandit..." -ForegroundColor Yellow
docker-compose run --rm web bandit -r . -x ./venv,./*/migrations/

# 7. Django Deployment Check
Write-Host "Running Django Deploy Check..." -ForegroundColor Yellow
docker-compose run --rm web python manage.py check --deploy

# 8. Migration Consistency Check
Write-Host "Running Migration Check..." -ForegroundColor Yellow
docker-compose run --rm web python manage.py makemigrations --check --dry-run

# Cleanup
docker-compose down

Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "✅ Validation passed successfully!" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray
