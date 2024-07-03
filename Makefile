.PHONY: install run lint test clean dev ensure-poetry

# Default goal
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
POETRY := poetry
PYTHONPATH := $(shell pwd)/src

# Export PYTHONPATH
export PYTHONPATH := $(PYTHONPATH)

# Ensure Poetry is installed
ensure-poetry:
	@if ! command -v $(POETRY) >/dev/null 2>&1; then \
		echo "Poetry could not be found. Installing..."; \
		curl -sSL https://install.python-poetry.org | $(PYTHON) -; \
		export PATH=$$HOME/.local/bin:$$PATH; \
	fi

# Help command
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install      Install dependencies using poetry"
	@echo "  run          Run the application"
	@echo "  lint         Lint the code using flake8"
	@echo "  test         Run tests using pytest"
	@echo "  clean        Clean up the project directory"
	@echo "  help         Show this help message"

# Install dependencies
install: ensure-poetry
	$(POETRY) install

# Lint the code
lint: ensure-poetry
	$(POETRY) run flake8 src/

# Run tests
test: ensure-poetry
	$(POETRY) run pytest

# Run the application
run: ensure-poetry
	$(POETRY) run gunicorn -w 4 -b 0.0.0.0:8000 main:flask_app

# Run app in dev mode
dev: ensure-poetry
	# Run the application
	$(POETRY) run gunicorn -w 4 -b 0.0.0.0:8000 main:flask_app --reload

# Clean up the project directory
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .tox
	rm -rf build
	rm -rf dist
	rm -rf .nox

# End of Makefile