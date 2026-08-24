import json
from pathlib import Path
import re

WORKOUTS_DIR = Path(".", "workouts")

def save_workouts_to_json(workouts, start_date, end_date, num_dates):
    """
    Save processed workouts to a JSON file.
    """
    filename = f"workouts_start_{start_date}_end_{end_date}_num_{num_dates}.json"
    file_path = Path(WORKOUTS_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(workouts, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(workouts)} workouts to {file_path}")


def load_workouts(filename):
    with open(filename, "r", encoding="utf-8") as f:
        workouts = json.load(f)
    print(f"Loaded {len(workouts)} workouts from {filename}")
    return workouts


def load_workouts_from_json(start_date, end_date, num_dates):
    """
    Load processed workouts from JSON file if it exists.
    Returns the list of workouts, or None if file not found.
    """
    filename = f"workouts_start_{start_date}_end_{end_date}_num_{num_dates}.json"
    file_path = Path(WORKOUTS_DIR, filename)
    if not file_path.exists():
        return None

    return load_workouts(file_path)

    


def load_cache(get_latest=False):
    # If we don’t know the cache filename in advance, we infer it by scanning for existing JSON files
    json_files = list(WORKOUTS_DIR.glob("workouts_start_*_end_*_num_*.json"))
    if not json_files:
        print("No cache files found. Run --update-cache first.")
        return None

    chosen_file = None

    # optionally, pick the latest file (todo: could sort by start_date or end_date)
    if get_latest:
        chosen_file = sorted(json_files)[-1]

    # pick file with largest num_*
    else:
        def _extract_num_days(path: Path) -> int:
            NUM_RE = re.compile(r"_num_(\d+)\.json$")
            m = NUM_RE.search(path.name)
            return int(m.group(1)) if m else -1
        chosen_file = max(json_files, key=_extract_num_days)

    return load_workouts(chosen_file), chosen_file