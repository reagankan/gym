<!-- kan-metadata
estimated_complexity: medium
estimated_iterations: 1-2
depends_on: [oracle-deploy, basic-auth]
rationale: A custom domain with HTTPS makes the gym tracker accessible via a memorable URL with encryption. Requires a domain name, DNS A record, and Let's Encrypt certificate via certbot. Must be done after basic-auth since nginx config builds on it.
-->

# Current State

- Gym tracker is live at http://141.148.236.230/ with basic auth (admin/admin)
- Server public IP: 141.148.236.230
- nginx listens on port 80
- OCI Security List allows TCP port 80 ingress

# Prerequisites (user must do manually before executing this prompt)

1. **Register a domain** — e.g. `reagankan.com`, `reagankan.dev`, `reagankan.xyz`, etc. Cheap options:
   - Namecheap, Cloudflare Registrar, Google Domains, Porkbun
   - `.xyz` domains are ~$1/year, `.com` ~$10/year
2. **Create a DNS A record** pointing the domain (or subdomain like `gym.reagankan.com`) to `141.148.236.230`
   - This is done in the domain registrar's DNS settings
   - TTL: 300 (5 min) for fast propagation during setup
3. **Add OCI Security List ingress rule** for port 443 (HTTPS):
   - Source CIDR: `0.0.0.0/0`, Protocol: TCP, Destination Port: `443`

**Tell the coder the chosen domain name before executing.** The placeholder below is `gym.reagankan.com`.

# Ask

## 1. Update `oracle/nginx-gym.conf` — add domain name and HTTPS

- Change `server_name _;` to `server_name gym.reagankan.com;` (replace with actual domain)
- Keep the port 80 server block but make it redirect to HTTPS:
  ```
  server {
      listen 80;
      server_name gym.reagankan.com;
      return 301 https://$host$request_uri;
  }
  ```
- Add a new HTTPS server block:
  ```
  server {
      listen 443 ssl;
      server_name gym.reagankan.com;
      ssl_certificate /etc/letsencrypt/live/gym.reagankan.com/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/gym.reagankan.com/privkey.pem;
      # ... existing proxy/auth/static config moves here ...
  }
  ```

## 2. Update `oracle/setup.sh` — install certbot and obtain certificate

- Install certbot: `apt install -y certbot python3-certbot-nginx`
- Obtain certificate: `certbot --nginx -d gym.reagankan.com --non-interactive --agree-tos -m <your-email>`
  - `--non-interactive` for scripted use
- Certbot auto-configures nginx SSL and sets up auto-renewal via systemd timer
- Open port 443 in iptables (same pattern as port 80: check before inserting)
- Persist iptables rules

## 3. Update `scripts/deploy.sh` — use domain for health check

- Change health check URL from `http://localhost/api/health` to `https://localhost/api/health` (or keep http://localhost since it's internal — certbot redirect only applies to external traffic)
- Actually: keep `http://localhost/api/health` since the redirect is for external `server_name` traffic, not localhost. No change needed here.

## 4. Update `README.md`

- Public URL: `https://gym.reagankan.com/`
- Note about domain registration and DNS setup
- Note about certificate auto-renewal (certbot handles this)
- How to manually renew: `sudo certbot renew`

## Notes

- Let's Encrypt certificates are free and auto-renew every 90 days
- Certbot's nginx plugin handles the SSL config automatically — the nginx config above is what it produces, but certbot may modify it further
- The HTTP → HTTPS redirect ensures all traffic is encrypted
- Basic auth over HTTPS means credentials are encrypted in transit (currently over HTTP they're base64-encoded in the clear)
- If the domain isn't ready yet, this prompt should be deferred
