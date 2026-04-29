# Log: web-server-bug-fix-macnotesapp

## T=1 (2026-04-29T17:28:49Z) — INIT
Seed prompt loaded. Plan created. Session start recorded.
Codebase fully read: server.py has inline HTML with two buttons. The "Update Data" button POSTs to /api/update-cache which fails on Linux due to macnotesapp stub.
Approach: Detect platform server-side via sys.platform, expose it to the client, disable button + add tooltip on non-darwin platforms.

## T=2 (2026-04-29T17:29:30Z) — CODE
### Coder Output
- Added `IS_MAC = sys.platform == "darwin"` constant
- HTML template uses `{{IS_MAC}}` placeholder, replaced in `index()` route
- JS disables btn-update on non-Mac with tooltip "Coming soon..."
- CSS `button:disabled` changed to `cursor: not-allowed`

## T=3 (2026-04-29T17:35:00Z) — REVIEW
### Reviewer Findings
- 🟢 Template replacement is safe (hardcoded true/false)
- 🟡 `post()` re-enables button on non-Mac (minor)
- No blockers for this task specifically

## T=4 (2026-04-29T17:35:00Z) — TEST
### Tester Output
- 2 new tests added: `test_index_contains_is_mac_false_on_linux`, `test_index_has_btn_update`
- All 11 tests pass

## T=5 (2026-04-29T17:39:00Z) — FIX + VERIFY
- Fixed `post()` finally block to not re-enable btn-update on non-Mac
- All 11 tests pass. Task COMPLETE.
