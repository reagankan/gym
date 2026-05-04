#!/bin/bash
set -e

KEY="${GYM_SSH_KEY:-$HOME/.ssh/oracle-gym.key}"
HOST="${GYM_HOST:-141.148.236.230}"
USER=ubuntu
SSH="ssh -i $KEY -o StrictHostKeyChecking=no $USER@$HOST"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Deploying gym tracker to $HOST ==="

# Sync files to server
rsync -az --delete \
    --exclude '.venv*' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.agents/' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    -e "ssh -i $KEY -o StrictHostKeyChecking=no" \
    "$SCRIPT_DIR/" "$USER@$HOST:/opt/gym/"

echo "Files synced."

# Install deps and restart
$SSH "cd /opt/gym && source venv/bin/activate && pip install -r requirements.txt --quiet && sudo systemctl restart gym-server"

echo "Service restarted. Waiting for startup..."
sleep 3

# Health check
HTTP_CODE=$($SSH "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/health")

if [ "$HTTP_CODE" = "200" ]; then
    echo "=== Deploy successful! (HTTP $HTTP_CODE) ==="
    echo "Public URL: http://$HOST/"
else
    echo "=== Deploy FAILED (HTTP $HTTP_CODE) ==="
    exit 1
fi
