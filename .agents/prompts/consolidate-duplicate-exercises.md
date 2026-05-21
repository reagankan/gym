### Context

Workout data lives in `workouts_start_*.json` at the project root. Each workout is a list: `[date_string, exercise_entry, exercise_entry, ...]` where each exercise entry is itself a list whose first element is the exercise name (a string) and whose remaining elements are set notes.

The dataset has ~724 unique exercise name strings across 338 workouts. Many are likely duplicates due to inconsistent capitalization, punctuation, abbreviation, and trailing periods — e.g. `"biceps."`, `"Biceps"`, `"Bicep"`, `"biceps. preacher."`, `"biceps. preacher machine."`, `"bicep preacher machine."`. Some variation is intentional: different machines or grips represent distinct tracking targets (e.g. `"pull-ups."` vs `"pull-ups. wide."` vs `"pull-ups. v grip."`).

### Ask

Build a tool that surfaces **potentially duplicate exercise names** for human review — not auto-merging, just flagging candidates.

The output should be a human-readable report (Markdown or terminal table) grouping names that are likely referring to the same exercise. For each group show:
- All the variant names
- How many times each appears in the dataset
- The date range each name spans (first and last workout date)

**Similarity signals to use** (combine as appropriate):
1. Case-insensitive exact match after stripping trailing punctuation/whitespace
2. One name is a prefix of another (e.g. `"biceps"` ↔ `"biceps. preacher."`)
3. Edit distance / fuzzy match for typos (e.g. `"chest fly."` ↔ `"chest flys."`)
4. Shared root word after removing modifiers like "seated", "standing", "machine", "cable", "barbell", "dumbbell"

**Do NOT merge** entries that differ by a meaningful machine/grip qualifier — flag these with a note like "possible separate tracking intent" so the human can decide. The point is to surface ambiguous cases, not to auto-resolve them.

Output the report to `.agents/checkpoints/consolidate-duplicate-exercises/report.md`.

### Constraints

- Read-only analysis — do not modify any JSON files
- Script should be reusable (we'll want to re-run it after any manual consolidation)
- Put the script at `scripts/find_duplicate_exercises.py`
- No new pip dependencies beyond what's already in `requirements.txt` — check first
