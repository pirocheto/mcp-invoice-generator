MCP_PORT ?= 8000

.PHONY: dev
dev:
	@echo "Run the MCP server in development mode with auto-reloading."
	fastmcp run app/main.py --transport http --port $(MCP_PORT) --reload

.PHONY: test
test:
	@echo "Run the test suite."
	coverage run -m pytest
	coverage report -m

.PHONY: build
build:
	@echo "Build the Docker image for the MCP server."
	podman build -t mcp:latest .

.PHONY: start
start:
	@echo "Start the MCP server using Podman. (Prod run)"
	podman run -p $(MCP_PORT):$(MCP_PORT) -e MCP_PORT=$(MCP_PORT) mcp:latest