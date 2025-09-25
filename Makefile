.PHONY: install lint format type-check test check run

install:
	pip install -r backend/requirements-dev.txt

lint:
	flake8 backend/

format:
	black backend/ && isort backend/

type-check:
	mypy backend/ || true

test:
	pytest -q

check: lint type-check test

run:
	python backend/manage.py runserver 0.0.0.0:8000
