# Variables
APP_NAME = playground
APP_VERSION = v0.1.0

# Install project dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI server
run:
	uvicorn main:app --reload

# Format code using black
format:
	chmod +x format.sh && ./format.sh

# Run unit tests using pytest
test:
	pytest tests/

# Phony targets
.PHONY: install run format test