# Task: web-server-bug-fix-macnotesapp
## Status: COMPLETE
## Current Phase: DONE
## Iteration: 1/3
## Project: /shared/user/gym
## Step: T=5
## Session Start: 2026-04-29T17:28:49Z
## Hours Elapsed: 0

## Seed Prompt
Server has "Update Data" button that errors on Linux with "macnotesapp not available". Autodetect platform and disable button with tooltip "Coming soon — macOS only".

## Milestones
- [x] Information retrieved
- [x] Initial implementation complete
- [x] Code review passed
- [x] Tests written and passing (11/11)
- [x] Final review clean
- [ ] Documentation updated (pending user approval)

## Current State
Complete. The "Update Data" button is disabled on non-macOS platforms with a tooltip. The `post()` function also won't re-enable it on non-Mac.

## Files Modified
- server.py (IS_MAC detection, HTML template injection, button disable logic)
- test_server.py (2 new tests: isMac=false check, btn-update presence)

## Unit Test Coverage
11 passed, 0 failed, 0 skipped

## Feature Flags / Disabled Code
None

## Open Issues
None
