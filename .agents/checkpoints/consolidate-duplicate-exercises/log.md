# Task Log: Find Duplicate Exercise Names

## T=1 (2026-05-21) — RETRIEVE
### Delegated to: orchestrator-direct-retrieval
### Task given: Understand data format, check requirements, explore codebase
### Result:
- Latest workout file: `workouts_start_20230308_end_20260416_num_437.json` (437 workouts, 706 unique exercise names)
- Data format: list of workouts; each workout is [date_string, [exercise_name, ...set_notes], ...]
- requirements.txt has only: flask, matplotlib, beautifulsoup4, gunicorn — stdlib only for fuzzy matching
- scripts/ dir has only deploy.sh
- stdlib `difflib.SequenceMatcher` available for fuzzy matching
- Some entries are notes/log text — need filtering heuristic
### Plan revision: None needed, proceed to CODE phase

## T=2 (2026-05-21) — RETRIEVE (orchestrator re-assessment)
### Delegated to: orchestrator-direct-review
### Task given: Assess quality of existing script and report
### Result:
- Script exists and runs correctly
- Report has significant noise:
  - P1: 674-entry group dominated by "done.", "done. <note>", "Left 60x5...", "left arm only."
  - P12: "Mohan 25", "Mohan 190" etc. (workout-buddy annotations, not exercises)
  - P15: "Reagan 30.", "Reagan 0x10." etc. (similar annotations)
  - P17: "seat 5.", "seat 6." etc. (machine seat settings, not exercises)
  - F2/F5/F9/F14: Date entries "April 25", "July 14" etc.
  - F11/F12: Time entries "start time. 1742."
  - F6: "chips." ↔ "hips." false positive
- `is_exercise_name()` needs stronger filtering
- Fuzzy threshold 0.82 may be too low for short names
### Plan revision: Improve is_exercise_name() and similarity logic, then re-run
