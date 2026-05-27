PYTHON ?= python
PIP ?= pip

.PHONY: install run test lint security reports clean docker-up docker-down

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) src/app.py

test:
	pytest -v --cov=src --cov-report=html:htmlcov

lint:
	ruff check src tests

security:
	bandit -r src -f json -o reports/bandit-report.json
	pip-audit -r requirements.txt -f json -o reports/pip-audit-report.json

reports:
	mkdir -p reports

clean:
	rm -rf .pytest_cache .ruff_cache reports htmlcov

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
