#!/usr/bin/env bash
echo "Hello from Project django_graph_db"

/llama-dir/llama-b8123/llama-server \
  -m "/models/model.gguf" \
  --embedding \
  --host "0.0.0.0" \
  --port "8080" &

uv run manage.py collectstatic --no-input
echo "running migrations"
uv run manage.py migrate --no-input
uv run gunicorn django_graph_db.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3 & nginx -g "daemon off;"