# Checkpoint 61: Multi-App Oracle Deployment — Gym App Fixes

## Goal
Make the gym app work behind an nginx reverse proxy at `/gym/` prefix by converting all hardcoded absolute URLs to relative URLs.

## Changes
1. **server.py** — Convert 4 absolute paths to relative:
   - `fetch('/api/process-cache-stream', ...)` → `fetch('api/process-cache-stream', ...)`
   - `fetch('/api/exercises')` → `fetch('api/exercises')`
   - `img.src = '/imgs/...'` → `img.src = 'imgs/...'`
   - `onclick="post('/api/update-cache', ...)"` → `onclick="post('api/update-cache', ...)"`
2. **oracle/nginx-gym.conf** — Add superseded-by comment for nginx-multi.conf

## Verification
- `python -c "import server; print('OK')"` passes
- `grep -n "fetch('/\|href=\"/" server.py` returns no matches
