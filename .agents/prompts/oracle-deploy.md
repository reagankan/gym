<!-- kan-metadata
estimated_complexity: medium
estimated_iterations: 1-2
depends_on: []
rationale: The gym tracker server currently runs locally. We need to deploy it to an Oracle Cloud Free Tier VM so it's accessible from a phone at the gym via a public URL. The VM already exists and has networking configured.
-->

# Current State

- `server.py` is a Flask app serving on port 8080 (configurable via `HOST`/`PORT` env vars)
- It serves a single-page UI with buttons to update data and generate exercise plots
- Dependencies: flask, matplotlib, beautifulsoup4 (in `requirements.txt`)
- The app reads/writes JSON cache files and generates PNG plots to `imgs/`
- No deployment infrastructure exists yet in this repo

## Oracle Cloud Instance (already provisioned)

- **Public IP**: 141.148.236.230
- **Shape**: VM.Standard.E2.1.Micro (Always Free tier)
- **Region**: eu-amsterdam-1
- **OS**: Ubuntu 20.04.6 LTS (Focal Fossa) Minimal
- **Python**: 3.8.10 (pre-installed)
- **RAM**: 1GB
- **Disk**: 45GB (42GB free)
- **User**: `ubuntu`
- **SSH key**: `~/shared/instance-keys/instance-20260207-0921/ssh-key-2026-02-07.key`
- **Source repo**: `~/shared/gym` (local, no GitHub remote)

## Firewall State (as discovered)

- iptables has a REJECT-all rule at position 5 — new ALLOW rules must be inserted before it
- Only port 22 (SSH) is currently allowed
- OCI Security List also needs an ingress rule for port 80 (done in console, not scriptable here)

# Ask

Deploy the gym tracker Flask server to this Oracle VM so it runs permanently with a public URL.

## 1. Create `oracle/gym-server.service` — systemd unit file

- `WorkingDirectory=/opt/gym`
- Uses gunicorn: `/opt/gym/venv/bin/gunicorn -w 2 -b 127.0.0.1:8080 server:app`
- `Restart=always`, `RestartSec=5`
- `After=network.target`
- Run as user `ubuntu`

## 2. Create `oracle/nginx-gym.conf` — nginx reverse proxy

- Listen on port 80
- Proxy pass to `127.0.0.1:8080`
- Standard proxy headers (`X-Forwarded-For`, `X-Forwarded-Proto`, `Host`)
- Serve `/imgs/` directly from `/opt/gym/imgs/` for performance (static file bypass)

## 3. Create `oracle/setup.sh` — one-time server initialization script

Run on the VM via SSH. Must be idempotent (safe to re-run).

- `apt update && apt install -y python3-venv python3-pip nginx`
- Create `/opt/gym` owned by `ubuntu`
- Create venv with `python3 -m venv /opt/gym/venv`
- Install requirements: `/opt/gym/venv/bin/pip install -r /opt/gym/requirements.txt`
- Copy systemd service file: `cp /opt/gym/oracle/gym-server.service /etc/systemd/system/`
- Copy nginx config: `cp /opt/gym/oracle/nginx-gym.conf /etc/nginx/sites-available/gym` and symlink to `sites-enabled/`, remove default site
- `systemctl daemon-reload && systemctl enable --now gym-server nginx`
- Open port 80 in iptables: `iptables -I INPUT 5 -p tcp --dport 80 -j ACCEPT` (insert before the REJECT rule)
- Persist iptables rules with `netfilter-persistent save` (install `iptables-persistent` if needed)
- Print status confirmation

## 4. Create `scripts/deploy.sh` — one-command deploy from local machine

- SSH key path: `~/shared/instance-keys/instance-20260207-0921/ssh-key-2026-02-07.key`
- Host: `141.148.236.230`, user: `ubuntu`
- `rsync -az --delete -e "ssh -i $KEY"` the repo to `ubuntu@$HOST:/opt/gym/`
- Exclude: `.venv*`, `__pycache__`, `.git`, `.agents/`, `*.pyc`, `.pytest_cache`
- SSH into the host and run:
  - `cd /opt/gym && source venv/bin/activate && pip install -r requirements.txt --quiet`
  - `sudo systemctl restart gym-server`
- Health check: wait 3 seconds, then `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/`
- Print success/failure based on HTTP status code

## 5. Add `/api/health` endpoint to `server.py`

- Returns `{"status": "ok", "timestamp": "...", "exercises": N}` where N is the count of PNGs in `imgs/`
- Used by deploy script health check and external monitoring

## 6. Add `gunicorn` to `requirements.txt`

## 7. Update `README.md` with deployment section

- Initial setup: rsync files to server, then `sudo bash /opt/gym/oracle/setup.sh`
- Deploy updates: `bash scripts/deploy.sh`
- Public URL: `http://141.148.236.230/`
- Check logs: `journalctl -u gym-server -f`
- Restart: `sudo systemctl restart gym-server`
- Note: OCI Security List must allow TCP port 80 ingress from 0.0.0.0/0 (configured in OCI console)

## Notes

- The "Update Data" button is already disabled on non-macOS. No changes needed.
- JSON cache files and `imgs/` are in the repo and will be rsynced. Plots can be regenerated via the UI.
- No HTTPS for now (can add Let's Encrypt later). No domain name yet.
- Python 3.8 is fine for all dependencies used.
- With 1GB RAM, 2 gunicorn workers is appropriate. Don't increase.
