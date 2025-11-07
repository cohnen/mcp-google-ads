# Makefile for MCP Google Ads Agent

# Python interpreter from venv
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

.PHONY: help setup run test clean lint format

help:
	@echo "📋 Available commands:"
	@echo "  make setup    - Create venv and install dependencies"
	@echo "  make run      - Run the MCP Google Ads server"
	@echo "  make test     - Run tests with pytest"
	@echo "  make clean    - Remove venv and cache files"
	@echo "  make lint     - Check code quality"
	@echo "  make format   - Format code with black (if installed)"

setup:
	@echo "🔧 Setting up virtual environment..."
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Setup complete! Copy .env.example to .env and configure your credentials."

run:
	@echo "🚀 Starting MCP Google Ads server..."
	$(PYTHON) google_ads_server.py

test:
	@echo "🧪 Running tests..."
	@if [ -f "$(PYTHON)" ]; then \
		if $(PIP) list | grep -q pytest; then \
			$(PYTHON) -m pytest -v; \
		else \
			echo "⚠️  pytest not installed. Installing..."; \
			$(PIP) install pytest; \
			$(PYTHON) -m pytest -v; \
		fi \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
	fi

test-basic:
	@echo "🧪 Running basic functionality test..."
	$(PYTHON) test_google_ads_mcp.py

test-auth:
	@echo "🔐 Testing authentication..."
	$(PYTHON) test_token_refresh.py

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

lint:
	@echo "🔍 Checking code quality..."
	@if $(PIP) list | grep -q flake8; then \
		$(PYTHON) -m flake8 google_ads_server.py; \
	else \
		echo "⚠️  flake8 not installed. Skipping..."; \
	fi

format:
	@echo "✨ Formatting code..."
	@if $(PIP) list | grep -q black; then \
		$(PYTHON) -m black google_ads_server.py; \
	else \
		echo "⚠️  black not installed. Skipping..."; \
	fi

# Development targets
install-dev:
	@echo "📦 Installing development dependencies..."
	$(PIP) install pytest flake8 black

# Check environment
check-env:
	@echo "🔍 Checking environment configuration..."
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
	else \
		echo "⚠️  .env file not found. Copy .env.example to .env"; \
	fi
	@if [ -d .venv ]; then \
		echo "✅ Virtual environment exists"; \
	else \
		echo "⚠️  Virtual environment not found. Run 'make setup'"; \
	fi

# Show Python version
version:
	@echo "🐍 Python version:"
	@$(PYTHON) --version
	@echo "\n📦 Installed packages:"
	@$(PIP) list
