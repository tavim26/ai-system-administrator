# Imagine de baza cu Python 3.11
FROM python:3.11-slim

# Directorul principal 
WORKDIR /app

# Instalarea dependintelor necesare MCP server
COPY docker/mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copierea codului MCP server in container
COPY src/mcp_server/ /app/mcp_server/

# Director montat pentru datele accesate de MCP
VOLUME ["/data"]

# Expune portul MCP
EXPOSE 8000

# Variabile folosite de serverul FastMCP
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Porneste serverul MCP prin modulul Python
CMD ["python", "-m", "mcp_server.server"]
