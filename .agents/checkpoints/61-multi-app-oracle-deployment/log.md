# Checkpoint 61: Log

## Actions Taken
- Read `server.py` and identified 4 hardcoded absolute URLs (2 fetch calls, 1 img.src, 1 onclick)
- Converted all 4 to relative URLs (no leading `/`)
- Added superseded-by comment to `oracle/nginx-gym.conf`
- Verified import succeeds and no absolute paths remain

## Result
All URLs in the gym app are now relative, so they resolve correctly when served behind `/gym/` prefix via nginx.
