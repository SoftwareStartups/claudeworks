.PHONY: install format lint typecheck check test clean all

# Install dependencies
install:
	uv sync

# Format code
format:
	ruff format .

# Lint code
lint:
	ruff check .

# Fix linting issues automatically
lint-fix:
	ruff check . --fix

# Type checking
typecheck:
	pyright

# Run all checks (lint + typecheck)
check: lint typecheck

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov

# Clean build artifacts and caches
clean:
	rm -rf .pytest_cache .ruff_cache .pyright __pycache__ .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Run all checks and tests
all: check test
