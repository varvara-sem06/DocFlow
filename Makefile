.PHONY: help install migrate run worker beat test lint format clean

help:
	@echo "install   — установить зависимости"
	@echo "migrate   — применить миграции"
	@echo "run       — запустить Django"
	@echo "worker    — запустить Celery worker"
	@echo "beat      — запустить Celery beat"
	@echo "test      — запустить тесты"
	@echo "lint      — ruff + black"
	@echo "clean     — удалить __pycache__, .pyc"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

worker:
	celery -A config worker -l info

beat:
	celery -A config beat -l info

test:
	pytest

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
