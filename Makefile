# Makefile for Meteorito Backend

.PHONY: build up down restart logs shell test lint ci migrate migrations format security check-deploy

build:
	docker-compose build

sync-deps:
	docker-compose build --no-cache web
	docker-compose up -d web

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web python manage.py shell

test:
	docker-compose exec web python manage.py test

lint:
	docker-compose exec web flake8 . --exclude=venv,*/migrations/*
	docker-compose exec web vulture . --min-confidence 80 --exclude venv,*/migrations/*
	docker-compose exec web bandit -r . -x ./venv,./*/migrations/
	docker-compose exec web mypy . --exclude 'venv|migrations'

format:
	docker-compose exec web isort .
	docker-compose exec web black .

migrate:
	docker-compose exec web python manage.py migrate

migrations:
	docker-compose exec web python manage.py makemigrations

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

ci: build
	docker-compose up -d db
	docker-compose run --rm web python manage.py test
	docker-compose run --rm web flake8 . --exclude=venv,*/migrations/*
	docker-compose run --rm web vulture . --min-confidence 80 --exclude venv,*/migrations/*
	docker-compose run --rm web bandit -r . -x ./venv,./*/migrations/
	docker-compose run --rm web python manage.py check --deploy
	docker-compose run --rm web python manage.py makemigrations --check --dry-run
	docker-compose down
