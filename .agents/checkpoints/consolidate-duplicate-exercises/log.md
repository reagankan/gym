# Task Log: Find Duplicate Exercise Names

## T=1 (2026-05-21) — RETRIEVE
### Delegated to: orchestrator-direct-retrieval
### Task given: Understand data format, check requirements, explore codebase
### Result:
- Latest workout file: `workouts_start_20230308_end_20260416_num_437.json` (437 workouts)
- Data format: list of workouts; each workout is [date_string, [exercise_name, ...set_notes], ...]
- requirements.txt: flask, matplotlib, beautifulsoup4, gunicorn only — stdlib for fuzzy matching
- stdlib `difflib.SequenceMatcher` available for fuzzy matching
### Plan revision: None needed, proceed to CODE phase

## T=2 (2026-05-21) — RETRIEVE (orchestrator re-assessment)
### Task given: Assess quality of existing script and report
### Result:
- Script runs but report has significant noise (831 names, 59 groups)
- Noise: "done." variants, Mohan/Reagan annotations, seat settings, date entries, time entries
- False positive fuzzy match: "chips." and "hips."
### Plan revision: Improve is_exercise_name() and similarity logic

## T=3 (2026-05-21) — CODE
### Task given: Improve filtering in scripts/find_duplicate_exercises.py
### Result:
- Rewrote NOTE_PATTERNS: date entries, mohan/reagan prefix, seat/time/location, left./right. notes
- Expanded NAME_STOPLIST: home, stop, left, right, just hang, two/three/four/five sets
- Added NOISE_PREFIXES for done/stop/home/left/right/after variants
- Added person-name filter including ryan
- Added \d+x\d+ anywhere pattern for embedded weight notation
- Fuzzy threshold 0.88, min-length guard at 8 chars
- Re-ran: 594 unique names, 43 groups — noise eliminated

## T=4 (2026-05-21) — ASSESS
### Result: COMPLETE
- Report contains only genuine exercise name variants
- All 4 similarity signals working correctly
- Qualifier-difference groups correctly flagged
- Script is reusable (CLI --input/--output/--threshold flags intact)
