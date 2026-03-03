.PHONY: dev
dev:
	@echo "Run the MCP server in development mode with auto-reloading."
	fastmcp run dev.fastmcp.json --reload

.PHONY: test
test:
	@echo "Run the test suite."
	coverage run -m pytest
	coverage report -m

.PHONY: build
build:
	@echo "Build the Docker image for the MCP server."
	docker build -t mcp:latest .

.PHONY: start
start:
	@echo "Start the MCP server using Docker. (Prod run)"
	docker run -p 8000:8000 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/outputs:/app/outputs \
		mcp:latest

.PHONY: run-inspector
run-inspector:
	@echo "Run the FastMCP inspector to monitor server performance and logs."
	bunx @modelcontextprotocol/inspector uv run fastmcp run dev.fastmcp.json


