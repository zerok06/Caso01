#!/bin/bash

# 1. Start Celery Worker in the background
# We capture the PID to kill it if the container stops
celery -A core.celery_app worker --loglevel=info &
CELERY_PID=$!

# 2. Start a dummy HTTP server to satisfy Cloud Run's port requirement
# Cloud Run expects the container to listen on $PORT (default 8080)
echo "Starting dummy HTTP server on port $PORT for Cloud Run health check..."
python -m http.server $PORT &
HTTP_PID=$!

# 3. Wait for any process to exit
# If Celery dies, we should exit so Cloud Run restarts us
wait -n $CELERY_PID $HTTP_PID

# Exit with the status of the process that exited first
exit $?
