<!-- kan-metadata
estimated_complexity: low
estimated_iterations: 1
depends_on: [oracle-deploy]
rationale: Basic auth protects the gym tracker from public access. This is simple nginx config — no domain or HTTPS needed. Do this first since it's fully self-contained.
-->

# Current State

- Gym tracker is live at http://<SERVER_IP>/ with no authentication
- nginx reverse proxies port 80 → gunicorn on 8080
- nginx config is at `oracle/nginx-gym.conf`
- Setup script is at `oracle/setup.sh`
- Deploy script is at `scripts/deploy.sh`

# Ask

Add HTTP Basic Authentication so the site requires a username/password to access.

## 1. Update `oracle/nginx-gym.conf` — add basic auth

- Add `auth_basic "Gym Tracker";` and `auth_basic_user_file /etc/nginx/.htpasswd;` to the `location /` block
- Also add it to the `location /imgs/` block (protect everything)
- Exception: add a `location = /api/health` block with `auth_basic off;` so the health endpoint remains unauthenticated (for monitoring tools like UptimeRobot)

## 2. Update `oracle/setup.sh` — create the htpasswd file

- Install `apache2-utils` (provides `htpasswd` command)
- Generate `/etc/nginx/.htpasswd` with user `admin` and password `admin`:
  `htpasswd -cb /etc/nginx/.htpasswd admin admin`
- Make it idempotent: overwrite if exists (`-c` flag does this)
- Set permissions: `chmod 640 /etc/nginx/.htpasswd && chown root:www-data /etc/nginx/.htpasswd`

## 3. Update `README.md` — document the auth

- Default credentials: admin / admin
- How to change the password: `sudo htpasswd /etc/nginx/.htpasswd admin`
- Note that /api/health is unauthenticated

## Notes

- admin:admin is intentionally simple — this is a personal gym tracker, not a bank. The auth is just to prevent random internet scanners from poking around.
- The health endpoint must remain open for deploy script health checks and external monitoring.
- After implementation, run `scripts/deploy.sh` and then re-run `oracle/setup.sh` on the server to create the htpasswd file and reload nginx.
