# ASO-Project
An AI agent that acts like a system administrator.



# --- Pornire/Oprire ---
docker-compose up -d                    # Porneste toate containerele
docker-compose down                     # Opreste toate containerele
docker-compose restart                  # Restart toate


# --- Build ---
docker-compose build                    # Build toate imaginile

# --- Monitorizare ---
docker-compose ps                       # Status containere
docker stats                            # Resurse (CPU, RAM)
docker logs aso-ollama --follow         # Loguri live



# --- Modele Ollama ---
docker exec aso-ollama ollama list      	 # Lista modele
docker exec aso-ollama ollama pull qwen2.5:7b    # Download model
docker exec aso-ollama ollama rm qwen2.5:7b      # Sterge model


# --- GPU ---
docker exec aso-ollama nvidia-smi       	   # Verifica GPU
docker logs aso-ollama | grep "inference compute"  # Verifica CUDA



# --- Test Servicii ---
curl http://localhost:8080              # Test ADK Web
curl http://localhost:8000/sse          # Test MCP Server
curl http://localhost:11434/api/tags    # Test Ollama


# --- Cleanup ---
docker-compose down -v                  # Sterge containere + volume
docker system prune -a                  # Cleanup complet


# --- Troubleshooting ---
docker logs aso-ollama --tail 50        # Verifica erori Ollama
docker logs aso-adk-web --tail 50       # Verifica erori Agent
docker logs aso-mcp-server --tail 50    # Verifica erori MCP



# === URLs ===
# ADK Web: http://localhost:8080
# MCP SSE: http://localhost:8000/sse
# Ollama:  http://localhost:11434