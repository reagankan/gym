# Log: web-server

## T=1 (2026-04-29T08:20:21Z) — INIT
Seed prompt loaded. Plan created. Project at /home/reaganka/shared/gym.

Key observations from codebase read:
- main.py has two CLI paths: `--update-cache` (Notes → JSON) and `--process-cache` (JSON → plots)
- notes_utils.py uses macnotesapp (macOS-only) — update-cache only works on macOS
- plot_utils.py saves PNGs to ./imgs/ directory
- Data is workout JSON files with exercise blocks containing weight×reps notation
- config.json defines rep_exercises (pull-ups, sit-ups, dips)
- Existing dependencies: macnotesapp, beautifulsoup4, matplotlib

## T=2 (2026-04-29T08:20:21Z) — RETRIEVE
### Retriever Findings
- **Framework**: Flask wins for this use case. Single dependency, built-in static file serving, built-in Jinja2 templating, battle-tested on AWS/Oracle free tiers.
- **Deployment**: SSH + pip install flask + systemd service or nohup. Open port in security group (AWS) or VCN security list + iptables (Oracle). Bind to 0.0.0.0, use port 8080 to avoid root.
- **Matplotlib headless**: MUST call `matplotlib.use('Agg')` before importing pyplot. Call `plt.close('all')` after saving to prevent memory leaks. Set `MPLBACKEND=Agg` env var as backup.
- **Oracle Cloud gotcha**: Must open ports in BOTH VCN security list AND OS-level firewall.

## T=3 (2026-04-29T08:25:04Z) — CODE (iteration 1)
### Coder Output
Created 2 new files (no existing files modified):
- **server.py**: Flask app with 5 routes (/, /api/update-cache, /api/process-cache, /api/exercises, /imgs/<filename>). Inline HTML UI with Update Data, Update Graphs buttons, exercise dropdown, image display. matplotlib.use('Agg') set before imports. macnotesapp stubbed for Linux portability. plt.close('all') after each plot. Configurable host/port via env vars.
- **requirements.txt**: flask, matplotlib, beautifulsoup4

Verification: `python -c "import server"` passes. All 5 routes confirmed registered.

## T=4 (2026-04-29T08:27:44Z) — REVIEW (iteration 1)
### Reviewer Findings
**BLOCKERS (3):**
1. plot_utils.py savefig missing .png extension — dropdown will be empty, process-cache returns 500
2. server.py macnotesapp stub: NotesApp=None → TypeError, not ImportError. except ImportError is dead code.
3. server.py XSS in showImg() — innerHTML with string concatenation

**WARNINGS (5):**
4. CWD dependency for config.json and cache file paths
5. `<path:filename>` should be `<filename>`
6. plt.close('all') not thread-safe (acceptable for personal server)
7. numpy missing from requirements.txt
8. No auth on endpoints (acceptable for personal server)

## T=5 (2026-04-29T08:27:44Z) — TEST (iteration 1)
### Tester Results
6 tests written, 6 passed. Tests document current (broken) behavior:
- test_index_returns_200_with_gym_tracker — PASSED
- test_api_exercises_returns_json_list — PASSED
- test_serve_existing_image — PASSED
- test_serve_nonexistent_image_returns_404 — PASSED
- test_process_cache_returns_200_and_generates_plots — PASSED (asserts 500 due to savefig bug)
- test_update_cache_fails_on_linux — PASSED (asserts TypeError from stub)

Bugs confirmed by tests: savefig .png extension, macnotesapp stub TypeError.

## T=6 (2026-04-29T08:27:44Z) — EVALUATE (iteration 1)
### Decision
LOOP BACK TO CODE. 3 blockers found:
1. Fix plot_utils.py savefig to append .png extension
2. Fix macnotesapp stub to provide clear error (not TypeError)
3. Fix XSS in showImg() — use DOM APIs
4. Fix CWD dependency — use script directory for file paths
5. Fix route to use `<filename>` not `<path:filename>`
Then update tests to assert correct behavior (200 for process-cache).

## T=7 (2026-04-29T08:31:26Z) — CODE (iteration 2)
### Coder Output
Applied 6 fixes to server.py and plot_utils.py:
1. plot_utils.py: Added `.png` extension to savefig path
2. server.py: macnotesapp stub now raises ImportError via _NotAvailable class
3. server.py: XSS fix — showImg() uses DOM APIs instead of innerHTML
4. server.py: Added PROJECT_DIR, os.chdir(PROJECT_DIR) for CWD independence
5. server.py: Changed `<path:filename>` to `<filename>`
6. server.py: Config loading uses PROJECT_DIR via os.chdir

## T=8 (2026-04-29T08:31:26Z) — TEST (iteration 2)
### Tester Results
6 tests rewritten and all pass:
- test_index_returns_200_with_gym_tracker — PASSED
- test_api_exercises_returns_json_list — PASSED
- test_serve_existing_image — PASSED
- test_serve_nonexistent_image_returns_404 — PASSED
- test_process_cache_generates_plots — PASSED ✅ (was 500, now 200 — .png fix confirmed)
- test_update_cache_fails_on_linux — PASSED ✅ (now ImportError, not TypeError — stub fix confirmed)

## T=9 (2026-04-29T08:32:24Z) — REVIEW (iteration 2)
### Reviewer Findings
**All 5 previous blockers verified fixed. No remaining blockers.**

Non-blocking warnings:
- plt.show() in plot_utils.py is no-op with Agg backend (acceptable)
- savefig uses relative path relying on os.chdir (acceptable since server.py controls entry)

**Verdict: ✅ COMPLETE — Ready to merge.**

## T=10 (2026-04-29T08:32:24Z) — EVALUATE (iteration 2)
### Decision
COMPLETE. All blockers resolved, all 6 tests pass, final review clean. Moving to DOCUMENT phase.

## T=11 (2026-04-29T08:33:14Z) — DOCUMENT
### Doc-Writer Output
Updated README.md with new "web server" section between usage and terminology. Documents: Flask install, server.py startup, three UI features, host/port configuration.

## T=12 (2026-04-29T08:33:14Z) — COMPLETE
Task complete. All milestones achieved in 2 iterations.

### Summary of Changes
**New files:**
- `server.py` — Flask web server (5 routes, inline HTML UI, macOS/Linux portable)
- `requirements.txt` — Minimal dependencies (flask, matplotlib, beautifulsoup4)
- `test_server.py` — 6 pytest tests, all passing

**Modified files:**
- `plot_utils.py` — Added `.png` extension to savefig (bug fix)
- `README.md` — Added web server documentation section
