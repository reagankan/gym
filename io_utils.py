import json
from pathlib import Path

def save_workouts_to_json(workouts, start_date, end_date, num_dates):
    """
    Save processed workouts to a JSON file.
    """
    filename = f"workouts_start_{start_date}_end_{end_date}_num_{num_dates}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(workouts, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(workouts)} workouts to {filename}")


def load_workouts_from_json(start_date, end_date, num_dates):
    """
    Load processed workouts from JSON file if it exists.
    Returns the list of workouts, or None if file not found.
    """
    filename = f"workouts_start_{start_date}_end_{end_date}_num_{num_dates}.json"
    file_path = Path(filename)
    if not file_path.exists():
        return None

    with open(filename, "r", encoding="utf-8") as f:
        workouts = json.load(f)
    print(f"Loaded {len(workouts)} workouts from {filename}")
    return workouts