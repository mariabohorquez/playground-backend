# Variables
APP_NAME = playground
APP_VERSION = v0.1.0

# Install project dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI server
run:
	cd app && uvicorn main:app --reload

# Format code using black
format:
	chmod +x format.sh && ./format.sh

# Run unit tests using pytest
test:
	pytest tests/

# This script should have the env variables for the project
local: 
	. local_setup.sh

# Phony targets
.PHONY: install run format test local