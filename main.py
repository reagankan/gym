from config_utils import refresh_config, get_config, ConfigKey
from notes_utils import get_notes
from parser_utils import parse_html, parse_workout
from date_utils import infer_workout_date_range
from io_utils import save_workouts_to_json, load_workouts_from_json, WORKOUTS_DIR, load_cache
from plot_utils import plot_exercise_boxplot
from stats_utils import remove_outliers

import argparse
import json
import re
from pathlib import Path
from typing import Tuple

DATE_PATTERN = re.compile(r"^2\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$")

def get_workouts():
    workouts = []
    for note in get_notes():
        try:
            if DATE_PATTERN.match(note.name):
                workouts.append(parse_workout(parse_html(note.body)))
            else:
                print("Skipping note", note.name)
        except Exception as e:
            print("Skipping note", note, e)
            continue

    return workouts

import re


# (?:\b(\d+(?:\.\d+)?)\s*)?   # optional number before x
# [xX]                        # literal x or X
# \s*                         # optional spaces
# (\d+(?:\.\d+)?)             # REQUIRED number after x
WEIGHT_RE = re.compile(r"(?:\b(\d+(?:\.\d+)?)\s*)?[xX]\s*(\d+(?:\.\d+)?)")

def parse_weight(line, parse_as_reps=False):
    """
    Format: someOptionalNumber{x,X}requiredNumber(optional suffix)

    Returns:
        - optional number before x if parse_as_reps=False
        - required number after x if parse_as_reps=True
    """
    m = WEIGHT_RE.search(line)
    if not m:
        return None

    if parse_as_reps:
        return float(m.group(2))  # requiredNumber

    before = m.group(1)  # someOptionalNumber (may be None)
    return float(before) if before is not None else None

from collections import defaultdict

def extract_exercise_weights(workouts, excerise_key):
    """
    Returns:
        dict[exercise_name][date] -> list[weights]
    """

    rep_exercises = get_config(ConfigKey.REP_EXERCISES)

    exercise_to_raw_map = defaultdict(set) # one to many
    raw_to_exercise_map = defaultdict(set) # many to one
    raw_to_date_map = defaultdict(set) # one to many


    data = defaultdict(lambda: defaultdict(list))

    for w in workouts:
        if not w:
            continue

        date = w[0]

        for block in w[1:]:
            if not isinstance(block, list) or not block:
                continue

            exercise = excerise_key(block[0])

            # I forget what edge case would have "done" be the start of a block.
            # if exercise in {"done.", "done"}:
            #     continue

            for line in block[1:]:
                weight = parse_weight(line, parse_as_reps=(rep_exercises and exercise in rep_exercises))
                if weight is not None and weight > 0:
                    data[exercise][date].append(weight)

                    exercise_to_raw_map[exercise].add(block[0])
                    raw_to_exercise_map[block[0]].add(exercise)
                    raw_to_date_map[block[0]].add(date)
                else:
                    print(f"weight is None or weight <= 0: {date}, {exercise}, {weight}")

    return data, exercise_to_raw_map, raw_to_exercise_map, raw_to_date_map

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

    parser.add_argument(
        "--process-cache",
        nargs="*",
        metavar="EXERCISE",
        help='Load workouts from cache. Optionally specify exercises (e.g. --process-cache "bench." "biceps." or "all")'
    )


    # read only operations (helpful for developing)
    parser.add_argument("--list", action="store_true", help="returns unique exercises")

    """
    "incline bench. dumbbells.", incline shoulder press.
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

    def _default_exercise_key(line):
        return line.strip().lower()


    args = parser.parse_args()

    if args.list:

        cache, _ = load_cache()
        exercises1, ev1, raw2exercisev1, raw2datev1 = extract_exercise_weights(cache, exercise_key=_default_exercise_key)



        # raw string --> exercise 

        # problem 1. many to one mapping.
        # currently, there are many raw strings that not mapped properly.
        # e.g. 'triceps. overhear cable.', 'triceps. bar pull-down.' are separate.
        # we'd want to be able to map them to the same 'triceps' exercise.

        # problem 2.
        # exercise has many levels.
        # <name> <variant 1> <variant 2>
        # --process-cache should let use match on name, then variants as deep as possible.
        # e.g. python main.py "biceps" will match all biceps
        # e.g. python main.py "biceps. ez curl." will match all biceps and then further match for just biceps on ez curl.


        from dataclasses import dataclass, field, InitVar
        from typing import Tuple

        @dataclass(frozen=True)
        class Exercise:
            raw: str
            tokens: Tuple[str, ...] = field(init=False)

            def __post_init__(self):
                # Process the raw string into tokens
                processed_tokens = tuple(
                    token.strip().rstrip(".") 
                    for token in self.raw.lower().strip().split(".")
                    if token.strip()
                )
                # hack: object.__setattr__ because frozen=True prevents normal assignment
                object.__setattr__(self, 'tokens', processed_tokens)

            def num_levels(self):
                return len(self.tokens)


        def _experimental_exercise_grouping_fn(line):
            return line.strip().rstrip(".")

        exercises2, ev2, raw2exercisev2, raw2datev2 = extract_exercise_weights(cache, excerise_key=Exercise)


        print(len(exercises1), len(ev1))
        print(len(exercises2), len(ev2))
        print()


        print("ev1: ", len(ev1))
        print("ev2: ", len(ev2))

        print("intersection: ", len(ev1.keys() & ev2.keys()))
        print("ev1 - ev2: ", len(ev1.keys() - ev2.keys()))
        print("ev2 - ev1: ", len(ev2.keys() - ev1.keys()))

        print(ev1.keys())


        assert(raw2exercisev1.keys() & raw2exercisev2.keys() == raw2exercisev1.keys())
        assert(raw2exercisev1.keys() & raw2exercisev2.keys() == raw2exercisev2.keys())



        top_to_raw = defaultdict(set)
        second_to_raw = defaultdict(set)
        third_to_raw = defaultdict(set)

        for i, (raw, exercise_set) in enumerate(raw2exercisev2.items()):

            if raw.lower().startswith("bicep"):
                v1 = raw2exercisev1.get(raw)
                v2 = raw2exercisev2.get(raw)

                v1_dates = raw2datev1.get(raw)
                v2_dates = raw2datev2.get(raw)

                print("=========")
                print(f"v1-raw: {raw} --> {v1}")
                print(f"v1 dates: {v1_dates}")
                print(f"v2-raw: {raw} --> {v2}")
                print(f"v2 dates: {v2_dates}")
                print("=========")

            assert(len(exercise_set) == 1)
            exercise = list(exercise_set)[0]

            n = exercise.num_levels()

            if n >= 1:
                top_to_raw[exercise.tokens[0]].add(raw)

            if n >= 2:
                second_to_raw[exercise.tokens[1]].add(raw)

            if n >= 3:
                third_to_raw[exercise.tokens[2]].add(raw)


        print(f"number of raw blocks: {len(raw2exercisev1)}")
        print(f"number of tier 1: {len(top_to_raw)}")
        print(f"number of tier 2: {len(second_to_raw)}")
        print(f"number of tier 3: {len(third_to_raw)}")


    if args.update_cache:
        print("Updating cache from Notes...")
        workouts = get_workouts()
        start_date, end_date, num_dates = infer_workout_date_range(workouts)
        save_workouts_to_json(workouts, start_date, end_date, num_dates)
        return None

    if args.process_cache is not None:


        # metadata: exercise mapping config
        EXERCISE_KEY = _default_exercise_key
        # EXERCISE_KEY = Exercise



        cache, cache_filename = load_cache()
        exercise_data, _ , _, _ = extract_exercise_weights(cache, excerise_key=EXERCISE_KEY)

        # TODO: find a smarter way to separate machines/movements or normalize into the same plot.
        # removing outliers across all dataset dates is inconsistent.
        # e.g. GOOD for "chest fly.", when I moved from chest fly cables to dumbells+bench.
        # e.g. BAD for "calf calves.", when I moved from standing to seated machines.
        # exercise_data = remove_outliers(exercise_data)

        show_plot = True
        if len(args.process_cache) == 0:
            exercises_to_plot = ["biceps."]
        elif len(args.process_cache) == 1 and args.process_cache[0].lower() == "all":
            exercises_to_plot = sorted(exercise_data.keys())
            show_plot=False
        else:
            exercises_to_plot = [e.lower() for e in args.process_cache]


        ### save stats
        stats_dict = {}



        ### save plots
        exercise_to_num_datapoints = {}
        for exercise in exercises_to_plot:
            if exercise in exercise_data:
                exercise_to_num_datapoints[exercise] = len(exercise_data[exercise])
                # plot_exercise_boxplot(exercise, exercise_data[exercise], show_plot=show_plot)

        import inspect
        src = inspect.getsource(EXERCISE_KEY)
        print(src)

        fn_hash = hash(src) # export PYTHONHASHSEED=0
        fn_hash_str = f"pos_{fn_hash}" if fn_hash >= 0 else f"neg_{-fn_hash}"

        file_path = Path(".", "stats", f"{cache_filename.name.strip(".json")}_{fn_hash_str}.json")
        with open(file_path, "w", encoding="utf-8") as f:

            stats_dict["exercise_key"] = {
                "hash": fn_hash,
                "hash_str": fn_hash_str,
                "src": src

            }
            stats_dict["exercise_to_num_datapoints"] = exercise_to_num_datapoints

            json.dump(stats_dict, f, ensure_ascii=False, indent=2)

        print(f"Saved {fn_hash_str} stats to {file_path}")


if __name__ == "__main__":
    refresh_config()
    main()



