# Imagine de baza cu Python 3.11
FROM python:3.11-slim

# Directorul principal
WORKDIR /app

# dependency-uri necesare ADK Web
COPY docker/adk-web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copierea agentului in structura de pachete a ADK
COPY src/agent/ /app/agents/quite_an_agent/

# Expunerea portului pentru interfata ADK Web
EXPOSE 8080

# Permite importuri din /app
ENV PYTHONPATH=/app

# Pornirea serverului ADK Web pe portul 8080
CMD ["adk", "web", "--port", "8080", "--host", "0.0.0.0", "agents"]
