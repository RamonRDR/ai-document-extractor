.PHONY: install run lint format typecheck test evaluate build
install:
	python -m pip install -e ".[dev]"
run:
	uvicorn document_extractor.api:app --reload
lint:
	ruff check .
	ruff format --check .
format:
	ruff check --fix .
	ruff format .
typecheck:
	mypy --ignore-missing-imports src/document_extractor
test:
	pytest -q
evaluate:
	python -m evaluation.runner --mode fixture --report evaluation-report.json
build:
	python -m build
