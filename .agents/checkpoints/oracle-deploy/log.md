# Log: oracle-deploy

## T=1 (2026-05-03T23:36:25Z) — INIT
Seed prompt loaded. Plan created. Session start recorded.
SSH access confirmed to <SERVER_IP> (ubuntu@, key at <SSH_KEY_PATH>).
Instance: Ubuntu 20.04, Python 3.8, 1GB RAM, 42GB free disk. Clean slate — no nginx, no /opt contents.
iptables REJECT-all at rule 5, only port 22 allowed. OCI Security List updated by user to allow port 80.

## T=2 (2026-05-03T23:37:30Z) — CODE
All 7 deliverables implemented by coder:
- oracle/gym-server.service, oracle/nginx-gym.conf, oracle/setup.sh
- scripts/deploy.sh
- server.py /api/health endpoint
- requirements.txt (gunicorn added)
- README.md deployment section
All files compile/syntax-check clean.

## T=3 (2026-05-03T23:38:00Z) — REVIEW + TEST (parallel)
### Review: 0 blockers, 6 warnings, 7 info
Top 3 actionable:
1. deploy.sh health check should use http://localhost/api/health (port 80, full stack)
2. gunicorn needs --timeout 120 for slow plot generation on 1GB VM
3. setup.sh should run nginx -t before restart

### Tests: 14/14 pass, 86% coverage
3 new tests added for /api/health endpoint. Full suite green.

## T=4 (2026-05-03T23:39:30Z) — CODE (iteration 2)
Applied 3 review fixes:
1. deploy.sh health check: http://localhost:8080/ → http://localhost/api/health
2. gym-server.service: added --timeout 120 to gunicorn
3. setup.sh: added nginx -t before systemctl restart nginx
Full test suite re-run: 14/14 pass.

## T=5 (2026-05-03T23:40:00Z) — DOCUMENT
Doc-writer verified README.md deployment section against all actual files. No changes needed — everything accurate.

## T=6 (2026-05-03T23:40:30Z) — COMPLETE
All deliverables done. 8 files created/modified. 14 tests passing. Ready to deploy.
