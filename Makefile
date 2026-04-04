.PHONY: install test lint format build publish clean

PYTHON := python3

install:
	$(PYTHON) -m pip install -e ".[dev]"

install-all:
	$(PYTHON) -m pip install -e ".[dev,web]"

test:
	pytest -v

test-cov:
	pytest --cov=bagualu --cov-report=html

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format . --check

typecheck:
	mypy bagualu

build:
	$(PYTHON) publish.py build

publish-test:
	$(PYTHON) publish.py test

publish:
	$(PYTHON) publish.py release

clean:
	rm -rf dist/ build/ *.egg-info bagualu.egg-info
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

all: clean lint test build

help:
	@echo "Available commands:"
	@echo "  make install        - Install development dependencies"
	@echo "  make install-all    - Install all dependencies (including web)"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make lint           - Run linter"
	@echo "  make format         - Format code"
	@echo "  make typecheck      - Run type checker"
	@echo "  make build          - Build package"
	@echo "  make publish-test   - Upload to TestPyPI"
	@echo "  make publish        - Upload to PyPI"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make all            - Clean, lint, test, and build"