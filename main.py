from notes_utils import get_notes
from parser_utils import parse_html, parse_workout
from date_utils import infer_workout_date_range
from io_utils import save_workouts_to_json, load_workouts_from_json

import argparse
import json
import re
from pathlib import Path

DATE_PATTERN = re.compile(r"^2\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$")

def get_workouts():
    notes = get_notes()
    workouts = [
        parse_workout(parse_html(note.body))
        for note in filter(lambda n: DATE_PATTERN.match(n.name), notes)
    ]
    return workouts

def demo():
    workouts = get_workouts()

    start_date, end_date, num_dates = infer_workout_date_range(workouts)
    print(f"Start: {start_date}, End: {end_date}, Count: {num_dates}")

    # Save or load JSON
    cached_workouts = load_workouts_from_json(start_date, end_date, num_dates)
    if cached_workouts is None:
        save_workouts_to_json(workouts, start_date, end_date, num_dates)
        workouts = load_workouts_from_json(start_date, end_date, num_dates)
    else:
        workouts = cached_workouts

    # Preview
    for i in range(5):
        print(workouts[i])


def main():
    parser = argparse.ArgumentParser(description="Gym workout processor")
    parser.add_argument("--update-cache", action="store_true", help="Fetch workouts from Notes and save to cache")
    parser.add_argument("--process-cache", action="store_true", help="Load workouts from cache")
    args = parser.parse_args()

    if args.update_cache:
        print("Updating cache from Notes...")
        workouts = get_workouts()
        start_date, end_date, num_dates = infer_workout_date_range(workouts)
        save_workouts_to_json(workouts, start_date, end_date, num_dates)
        return

    if args.process_cache:
        # If we don’t know the cache filename in advance, we infer it by scanning for existing JSON files
        json_files = list(Path(".").glob("workouts_start_*_end_*_num_*.json"))
        if not json_files:
            print("No cache files found. Run --update-cache first.")
            return

        # Pick the latest file (optional: could sort by start_date or end_date)
        latest_file = sorted(json_files)[-1]
        print(f"Processing cache: {latest_file}")
        with open(latest_file, "r", encoding="utf-8") as f:
            workouts = json.load(f)

        for i in range(5):
            print(workouts[i])
        return


if __name__ == "__main__":
    main()



