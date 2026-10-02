#!/bin/bash

# Porneste serverul Ollama in background
ollama serve &

# Asteapta ca serverul sa porneasca
sleep 5

# Descarca modelul
ollama pull qwen2.5:7b

wait
