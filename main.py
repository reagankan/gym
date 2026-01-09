from notes_utils import get_notes
from parser_utils import parse_html, parse_workout
from date_utils import infer_workout_date_range
from io_utils import save_workouts_to_json, load_workouts_from_json
from plot_utils import plot_exercise_boxplot
from stats_utils import remove_outliers

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

import re

WEIGHT_RE = re.compile(r"(\d+(\.\d+)?)x")

def parse_weight(line):
    """
    Returns float weight if present, else None
    """
    m = WEIGHT_RE.search(line)
    if not m:
        return None
    return float(m.group(1))

from collections import defaultdict

def extract_exercise_weights(workouts):
    """
    Returns:
        dict[exercise_name][date] -> list[weights]
    """

    data = defaultdict(lambda: defaultdict(list))

    for w in workouts:
        if not w:
            continue

        date = w[0]

        for block in w[1:]:
            if not isinstance(block, list) or not block:
                continue

            exercise = block[0].strip().lower()

            if exercise in {"done.", "done"}:
                continue

            for line in block[1:]:
                weight = parse_weight(line)
                if weight is not None and weight > 0:
                    data[exercise][date].append(weight)

    return data

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

    """
    "incline bench. dumbbells.",
    "bench.",
    "biceps.",
    "chest fly.",
    "abs core."
    "calf calves."
    "shoulders."
    "seated leg press."
    "triceps."
    "lat pull-down."
    "lat pulldown."
    "chest fly."
    "forearms."
    "seated pec dec."
    "bicep preacher machine."
    """
    parser.add_argument(
        "--exercises",
        nargs="+",
        default=["biceps."],
        help='Exercise names to plot (e.g. "bench." "biceps.") or "all"'
    )


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

        json_files = list(Path(".").glob("workouts_start_*_end_*_num_*.json"))
        if not json_files:
            print("No cache files found. Run --update-cache first.")
            return

        NUM_RE = re.compile(r"_num_(\d+)\.json$")
        def extract_num_days(path: Path) -> int:
            m = NUM_RE.search(path.name)
            return int(m.group(1)) if m else -1

        # pick file with largest num_*
        chosen_file = max(json_files, key=extract_num_days)

        # # Pick the latest file (optional: could sort by start_date or end_date)
        # chosen_file = sorted(json_files)[-1]


        print(f"Processing cache: {chosen_file}")
        with open(chosen_file, "r", encoding="utf-8") as f:
            workouts = json.load(f)

        for i in range(5):
            print(workouts[i])


        exercise_data = extract_exercise_weights(workouts)

        # TODO: find a smarter way to separate machines/movements or normalize into the same plot.
        # removing outliers across all dataset dates is inconsistent.
        # e.g. GOOD for "chest fly.", when I moved from chest fly cables to dumbells+bench.
        # e.g. BAD for "calf calves.", when I moved from standing to seated machines.
        # exercise_data = remove_outliers(exercise_data)


        if args.exercises is None:
            print("No exercises specified. Use --exercises or 'all'.")
            return

        if len(args.exercises) == 1 and args.exercises[0].lower() == "all":
            exercises_to_plot = sorted(exercise_data.keys())
        else:
            exercises_to_plot = [e.lower() for e in args.exercises]

        for exercise in exercises_to_plot:
            if exercise in exercise_data:
                plot_exercise_boxplot(exercise, exercise_data[exercise])


if __name__ == "__main__":
    main()



