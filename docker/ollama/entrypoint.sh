#!/bin/bash
set -e

# Start the Ollama server in the background
ollama serve &
SERVER_PID=$!

# Wait until the server responds (instead of a fixed sleep)
until ollama list >/dev/null 2>&1; do
  sleep 1
done

# Pull the model (no-op if it is already in the volume)
ollama pull "${OLLAMA_MODEL:-qwen2.5:7b}"

# Keep the container running as long as the server runs
wait $SERVER_PID