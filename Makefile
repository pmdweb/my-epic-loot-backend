.PHONY: install lint format type-check test check run

install:
	pip install -r requirements-dev.txt

lint:
	flake8 .

format:
	black . && isort .

type-check:
	mypy . || true

test:
	pytest -q

check: lint type-check test

run:
	python manage.py runserver 0.0.0.0:8000
