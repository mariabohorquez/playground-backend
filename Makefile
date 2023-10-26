# Install project dependencies
local:
	chmod +x local_setup.sh && ./local_setup.sh


install:
	pip install -r requirements.txt

# Run the FastAPI server
run:
	cd app && uvicorn main:app --reload

# Format code using black
lint:
	chmod +x format.sh && ./format.sh

# Run unit tests using pytest
test:
	pytest tests/

# Phony targets
.PHONY: install run lint test local
