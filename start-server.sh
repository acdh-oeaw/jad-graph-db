#!/usr/bin/env bash
echo "Hello from Project django_graph_db"

# Start ollama service in background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 5

# Pull the nomic-embed-text model from Hugging Face
echo "Pulling nomic-embed-text-v1.5 model..."
ollama pull nomic-embed-text

uv run manage.py collectstatic --no-input
echo "running migrations"
uv run manage.py migrate --no-input
uv run gunicorn django_graph_db.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3 & nginx -g "daemon off;"