#!/bin/bash
set -e

# Replicate the logic from the Makefile's "ci" target.
echo "Starting Backend Validation..."

# 1. Build the base image
docker-compose build

# 2. Ensure the database is up
docker-compose up -d db

# 3. Run Tests
echo "Running Tests..."
docker-compose run --rm web python manage.py test

# 4. Run Lint (Flake8)
echo "Running Flake8..."
docker-compose run --rm web flake8 . --exclude=venv,*/migrations/*

# 5. Run Dead Code Analysis (Vulture)
echo "Running Vulture..."
docker-compose run --rm web vulture . --min-confidence 80 --exclude venv,*/migrations/*

# 6. Run Security Audit (Bandit)
echo "Running Bandit..."
docker-compose run --rm web bandit -r . -x ./venv,./*/migrations/

# 7. Django Deployment Check
echo "Running Django Deploy Check..."
docker-compose run --rm web python manage.py check --deploy

# 8. Migration Consistency Check
echo "Running Migration Check..."
docker-compose run --rm web python manage.py makemigrations --check --dry-run

# Cleanup
docker-compose down

echo "----------------------------------------"
echo "✅ Validation passed successfully!"
echo "----------------------------------------"
