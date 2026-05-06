<!-- kan-metadata
estimated_complexity: low-medium
estimated_iterations: 1
depends_on: [oracle-deploy, basic-auth]
rationale: After deploying the arbitrage repo, nginx-multi.conf now serves the gym app under /gym/ instead of /. The exercise selector is empty, meaning either the imgs/ directory on the server is empty or the API/static paths are broken under the /gym/ prefix. Fix must not break the arbitrage deployment which owns nginx-multi.conf.
-->

# Current State

- Gym app is served under `/gym/` via `nginx-multi.conf` (owned by the arbitrage repo at `~/shared/arbitrage`)
- A separate agent recently deployed the arbitrage repo to the same Oracle instance. That deploy replaced the nginx config (switching from the gym-only config to `nginx-multi.conf`), which moved the gym app from `/` to `/gym/`. This is the most likely cause of the breakage.
- **The arbitrage repo at `~/shared/arbitrage` contains useful context** — check its recent commits, deploy script, and oracle/ directory to understand what changed on the server. Key files: `scripts/deploy.sh`, `oracle/nginx-multi.conf`, `oracle/ORACLE.md`. Recent relevant commits include the nginx-multi switch and basic auth addition.
- The arbitrage deploy script (`~/shared/arbitrage/scripts/deploy.sh`) deploys `nginx-multi.conf` and removes the old gym nginx site (`rm -f /etc/nginx/sites-enabled/gym`)
- The gym deploy script (`scripts/deploy.sh`) rsyncs to `/opt/gym/` with `--delete` and restarts `gym-server`
- The exercise selector dropdown shows no exercises (empty list from `/gym/api/exercises`)
- The gym server runs on port 8080, arbitrage dashboard on port 5000
- nginx-multi.conf rewrites `/gym/(.*)` → `/$1` before proxying to port 8080
- Frontend uses relative URLs (`api/exercises`, `imgs/...`) which resolve correctly under `/gym/`

## nginx-multi.conf (from arbitrage repo, DO NOT MODIFY)

```
location /gym/ {
    auth_basic "Gym Tracker";
    auth_basic_user_file /etc/nginx/.htpasswd;
    rewrite ^/gym(/.*)$ $1 break;
    proxy_pass http://127.0.0.1:8080;
    ...
}
location /gym/imgs/ {
    auth_basic "Gym Tracker";
    auth_basic_user_file /etc/nginx/.htpasswd;
    alias /opt/gym/imgs/;
}
location = /gym/api/health {
    auth_basic off;
    rewrite ^/gym(/.*)$ $1 break;
    proxy_pass http://127.0.0.1:8080;
}
```

## Gym deploy script health check (currently broken)

```bash
HTTP_CODE=$($SSH "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/health")
```

This hits `/api/health` at the root, but nginx-multi.conf no longer has a root handler — the gym health endpoint is now at `/gym/api/health`.

# Ask

Diagnose and fix why the exercise selector is empty. The root cause is likely one or more of:

1. **`/opt/gym/imgs/` is empty on the server** — the gym deploy's `rsync --delete` may have wiped server-generated PNGs that don't exist locally, OR the imgs were never synced properly
2. **Health check URL is wrong** — `scripts/deploy.sh` checks `http://localhost/api/health` but it should be `http://localhost/gym/api/health`
3. **The gym server's working directory or IMGS_DIR is wrong** after deploy

## Steps

### 1. SSH into the server and diagnose

- Check if `/opt/gym/imgs/` has any `.png` files: `ls /opt/gym/imgs/*.png | wc -l`
- Check gym-server status: `systemctl status gym-server`
- Check gym-server logs: `journalctl -u gym-server -n 50 --no-pager`
- Test the API directly: `curl http://127.0.0.1:8080/api/exercises`
- Test through nginx: `curl http://localhost/gym/api/exercises`

### 2. Fix `scripts/deploy.sh`

- Update health check URL from `http://localhost/api/health` to `http://localhost/gym/api/health`
- The rsync should NOT delete `imgs/` on the server if it contains server-generated plots that don't exist locally. Add `--exclude 'imgs/'` to the rsync command so server-side generated plots are preserved.

### 3. Regenerate plots on server (if imgs/ is empty)

- SSH in and trigger plot generation: `curl -X POST http://127.0.0.1:8080/api/process-cache` (or use the stream endpoint)
- This requires a workouts JSON cache file to exist in `/opt/gym/`. Check if one exists: `ls /opt/gym/workouts_start_*.json`
- If no cache file exists, the imgs/ from the local repo need to be synced. In that case, do a one-time rsync of just the imgs: `rsync -az -e "ssh -i $KEY" imgs/ $USER@$HOST:/opt/gym/imgs/`

### 4. Update `oracle/nginx-gym.conf` comment

The file already has a comment saying it's superseded. No changes needed to this file — it's not active on the server.

## Constraints

- **DO NOT modify anything in the arbitrage repo** (`~/shared/arbitrage/`)
- **DO NOT modify `nginx-multi.conf`** — it's owned by the arbitrage repo
- The fix must be entirely within the gym repo (`~/shared/gym/`)
- After fixing, both `~/shared/gym/scripts/deploy.sh` and `~/shared/arbitrage/scripts/deploy.sh` must work independently without breaking each other

## Verification

- `curl http://127.0.0.1:8080/api/exercises` returns a non-empty JSON array
- `curl http://localhost/gym/api/exercises` returns the same (through nginx)
- The web UI at `http://<IP>/gym/` shows exercises in the dropdown
- `bash scripts/deploy.sh` completes with "Deploy successful"
