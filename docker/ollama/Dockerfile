# Imagine de baza pentru Ollama server
FROM ollama/ollama:latest

# Expune portul API Ollama
EXPOSE 11434

# Copierea script de pornire si initializare model
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ruleaza script custom ca entrypoint
ENTRYPOINT ["/entrypoint.sh"]
