# Task: Find Duplicate Exercise Names
## Status: IN_PROGRESS
## Current Phase: RETRIEVE
## Iteration: 1/50

## Goals (from task)
Build a reusable script at `scripts/find_duplicate_exercises.py` that:
- Reads workout JSON files and extracts unique exercise name strings
- Groups potential duplicates using 4 similarity signals
- Outputs a human-readable Markdown report to `.agents/checkpoints/consolidate-duplicate-exercises/report.md`
- Each group shows: variant names, count per name, date range per name
- Flags groups with machine/grip qualifiers as "possible separate tracking intent"
- No new pip dependencies beyond requirements.txt (flask, matplotlib, beautifulsoup4, gunicorn)

## Plan
1. [DONE] Script exists at `scripts/find_duplicate_exercises.py`
2. [DONE] Report exists at `.agents/checkpoints/consolidate-duplicate-exercises/report.md`
3. [IN_PROGRESS] Assess report quality — many non-exercise entries leaking through:
   - "done.", "Left 60x5. Elbow hurts", "Mohan 25", "Reagan 30.", "seat 5.", "April 25"
   - False fuzzy matches: "chips." ↔ "hips."
   - Huge P1 catch-all bucket (674 appearances of "done." variants)
4. Improve filtering heuristics in `is_exercise_name()`
5. Improve similarity signals to reduce false positives
6. Re-run script and verify report quality
7. Document

## Current State
- Script runs and produces output
- Report has significant noise: non-exercise entries pass the filter
- Need better `is_exercise_name()` filtering and tighter similarity thresholds

## Files Modified
- `scripts/find_duplicate_exercises.py` (exists, needs improvement)
- `.agents/checkpoints/consolidate-duplicate-exercises/report.md` (exists, needs regeneration)

## Test Results
- Script runs without errors
- Report has quality issues (false positives, noise entries)

## Open Issues
- `is_exercise_name()` too permissive — lets through notes, date entries, set notations
- Fuzzy threshold 0.82 catching too many false positives (chips/hips)
- Large groups formed by union-find chaining through weak links
