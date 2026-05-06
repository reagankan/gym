# Task: fix-gym-under-subpath
## Status: COMPLETE
## Current Phase: DONE
## Iteration: 1/3
## Project: /shared/user/gym
## Step: T=8
## Session Start: 2026-05-05T03:28:01Z
## Hours Elapsed: 0

## Seed Prompt
Fix gym app broken under /gym/ subpath after arbitrage deploy moved it from root. Exercise selector empty. Fix deploy script health check URL, add rsync --exclude for imgs/, and regenerate plots if needed.

## Milestones
- [x] Information retrieved (server diagnosis)
- [x] Initial implementation complete
- [x] Code review passed
- [x] Tests written and passing
- [x] Final review clean
- [x] Documentation updated

## Current State
DONE. All fixes applied, deployed, and verified.

## Files Modified
- `scripts/deploy.sh` — added `--exclude 'imgs/'` to rsync, fixed health check URL to `/gym/api/health`
- `README.md` — updated deployment section to reflect /gym/ subpath

## Unit Test Coverage
14 passed, 0 failed, 0 skipped

## Feature Flags / Disabled Code
(none)

## Open Issues
(none)
