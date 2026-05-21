#!/usr/bin/env python3
"""
find_duplicate_exercises.py

Surfaces potentially duplicate exercise names in workout JSON files for human review.
Does NOT modify any data — read-only analysis.

Usage:
    python scripts/find_duplicate_exercises.py [--input PATH] [--output PATH]

Defaults:
    --input: most-recently-modified workouts_start_*.json in the project root
    --output: .agents/checkpoints/consolidate-duplicate-exercises/report.md
"""

import argparse
import difflib
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Modifiers whose presence indicates a meaningful qualifier (grip, equipment, angle).
# Groups containing names that differ ONLY by these words get a special flag.
QUALIFIER_WORDS = {
    "seated",
    "standing",
    "machine",
    "cable",
    "barbell",
    "dumbbell",
    "dumbbells",
    "incline",
    "decline",
    "flat",
    "wide",
    "narrow",
    "close",
    "grip",
    "bar",
    "ez",
    "band",
    "bands",
    "resistance",
    "hammer",
    "reverse",
    "overhead",
    "behind",
    "single",
    "one",
    "arm",
    "leg",
    "hand",
    "alternating",
    "both",
    "low",
    "high",
    "mid",
    "upper",
    "lower",
    "bent",
    "straight",
    "neutral",
    "supinated",
    "pronated",
    "lateral",
    "front",
    "rear",
    "back",
    "side",
    "preacher",
    "concentration",
    "cross",
    "cable",
    "rope",
    "pulley",
    "assisted",
    "weighted",
    "unweighted",
    "slow",
    "iso",
    "isometric",
    "pause",
    "tempo",
    "v",
    "y",
    "w",
    "t",
}

# Heuristics to detect note/log entries that are not exercise names.
NOTE_PATTERNS = [
    re.compile(r"^https?://"),
    re.compile(r"^\d+x\d+"),                       # set notation like "90x8"
    re.compile(r"^0x\d+"),                          # bodyweight set
    re.compile(r"^\d+\.\d+\s"),                     # decimal weight
    re.compile(r"goal\.", re.I),
    re.compile(r"push hard", re.I),
    re.compile(r"nothing\.", re.I),
    re.compile(r"lower back bent", re.I),
    # Date entries: "Aug 7", "August 21", "April03", "July 30", "April6"
    re.compile(
        r"^(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*\d",
        re.I,
    ),
    # Person-name + weight notation: "Mohan 25", "Reagan 100x10x2. 115x6"
    re.compile(r"^[A-Z][a-z]+\s+\d"),
    # Date-code like "April03", "April5"
    re.compile(r"^[A-Z][a-z]+\d+$"),
]

# Exact normalised names that are end-of-workout markers, not exercises.
NAME_STOPLIST = frozenset({"done", "home"})

MAX_EXERCISE_NAME_LEN = 60


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def find_latest_workout_file(root_dir: str) -> str:
    """Return the workout file with the most workouts (highest num_ value)."""
    pattern = os.path.join(root_dir, "workouts_start_*.json")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No workout files found matching {pattern}")

    def num_workouts(path: str) -> int:
        m = re.search(r"_num_(\d+)", os.path.basename(path))
        return int(m.group(1)) if m else 0

    return max(files, key=num_workouts)


def is_exercise_name(s: str) -> bool:
    """Return True if string looks like an exercise name rather than a note."""
    if not s or not isinstance(s, str):
        return False
    if len(s) > MAX_EXERCISE_NAME_LEN:
        return False
    for pat in NOTE_PATTERNS:
        if pat.search(s):
            return False
    # Stoplist: end-of-workout markers and other non-exercise tokens
    if normalise(s) in NAME_STOPLIST:
        return False
    # "two sets", "three sets" etc. are not exercise names
    if re.match(r"^(two|three|four|five)\s+sets?\.?$", s, re.I):
        return False
    # Names that end with a person's name or a note word are workout log entries
    # e.g. "Bicep Mohan.", "Biceps sore."
    if re.search(r"\b(mohan|reagan|sore|hurt|hurts|elbow|wrist|pain)\b", s, re.I):
        return False
    # Context notes: "after a nap.", "after nap.", "Gym may 21"
    if re.match(r"^after\b", s, re.I):
        return False
    if re.match(r"^gym\s+(may|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b", s, re.I):
        return False
    # Variants of "done" with trailing notes
    if re.match(r"^done\b", s, re.I):
        return False
    return True


def load_exercise_stats(path: str) -> Dict[str, Dict]:
    """
    Parse workout JSON and return a dict:
        name -> {count: int, dates: [str]}
    where dates are YYYYMMDD strings.
    """
    with open(path) as f:
        data = json.load(f)

    stats: Dict[str, Dict] = {}
    for workout in data:
        if not isinstance(workout, list) or not workout:
            continue
        date = workout[0]
        for entry in workout[1:]:
            if not isinstance(entry, list) or not entry:
                continue
            name = entry[0]
            if not is_exercise_name(name):
                continue
            if name not in stats:
                stats[name] = {"count": 0, "dates": []}
            stats[name]["count"] += 1
            stats[name]["dates"].append(date)

    return stats


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def strip_trailing_punct(s: str) -> str:
    """Remove trailing punctuation and whitespace."""
    return s.rstrip(". \t")


def normalise(s: str) -> str:
    """Lowercase + strip trailing punct/whitespace for exact-match comparison."""
    return strip_trailing_punct(s).lower()


def tokenize(s: str) -> List[str]:
    """Split a normalised name into word tokens."""
    # Replace punctuation with spaces, then split
    cleaned = re.sub(r"[.\-/,;:]+", " ", normalise(s))
    return [t for t in cleaned.split() if t]


def root_tokens(tokens: List[str]) -> frozenset:
    """Return tokens with qualifier words removed."""
    return frozenset(t for t in tokens if t not in QUALIFIER_WORDS)


def has_qualifier_difference(tokens_a: List[str], tokens_b: List[str]) -> bool:
    """
    True if the two token lists differ only in qualifier words — meaning
    the extra tokens in either list are all qualifiers.
    """
    set_a = frozenset(tokens_a)
    set_b = frozenset(tokens_b)
    only_in_a = set_a - set_b
    only_in_b = set_b - set_a
    return (
        bool(only_in_a or only_in_b)
        and only_in_a.issubset(QUALIFIER_WORDS)
        and only_in_b.issubset(QUALIFIER_WORDS)
    )


# ---------------------------------------------------------------------------
# Similarity signals
# ---------------------------------------------------------------------------

def exact_normalised_match(a: str, b: str) -> bool:
    """Signal 1: case-insensitive exact match after stripping trailing punct."""
    return normalise(a) == normalise(b)


def is_prefix_of(a: str, b: str) -> bool:
    """Signal 2: normalised a is a prefix of normalised b (or vice versa)."""
    na, nb = normalise(a), normalise(b)
    return nb.startswith(na + " ") or nb.startswith(na + ".") or na == nb


def prefix_match(a: str, b: str) -> bool:
    return is_prefix_of(a, b) or is_prefix_of(b, a)


def edit_distance_similar(a: str, b: str, threshold: float = 0.88) -> bool:
    """
    Signal 3: fuzzy edit-distance similarity via difflib SequenceMatcher.
    Uses normalised strings. Threshold 0.88 catches single-char typos on
    multi-word exercise names while avoiding false positives on short strings.
    Short names (< 8 chars normalised) are skipped — too collision-prone.
    """
    na, nb = normalise(a), normalise(b)
    if max(len(na), len(nb)) == 0:
        return False
    # Skip very short names — single-char edits cause too many false positives
    if min(len(na), len(nb)) < 8:
        return False
    # Skip if length ratio is too extreme — likely prefix/modifier difference
    ratio = len(min(na, nb, key=len)) / len(max(na, nb, key=len))
    if ratio < 0.6:
        return False
    return difflib.SequenceMatcher(None, na, nb).ratio() >= threshold


def shared_root_match(a: str, b: str) -> bool:
    """
    Signal 4: both names share the same root tokens after removing qualifiers.
    At least one token must survive in each, and roots must match exactly.
    """
    tok_a = tokenize(a)
    tok_b = tokenize(b)
    roots_a = root_tokens(tok_a)
    roots_b = root_tokens(tok_b)
    if not roots_a or not roots_b:
        return False
    return roots_a == roots_b and tok_a != tok_b  # must actually differ


def are_similar(a: str, b: str) -> bool:
    """Return True if any similarity signal fires."""
    return (
        exact_normalised_match(a, b)
        or prefix_match(a, b)
        or edit_distance_similar(a, b)
        or shared_root_match(a, b)
    )


# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------

def build_similarity_groups(names: List[str]) -> List[List[str]]:
    """
    Union-Find grouping: each name starts in its own group; merge when similar.
    Returns list of groups (each group is a list of names), singletons excluded.
    """
    parent = {n: n for n in names}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    n = len(names)
    for i in range(n):
        for j in range(i + 1, n):
            if are_similar(names[i], names[j]):
                union(names[i], names[j])

    groups: Dict[str, List[str]] = defaultdict(list)
    for name in names:
        groups[find(name)].append(name)

    return [sorted(g) for g in groups.values() if len(g) > 1]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def format_date(d: str) -> str:
    """Format YYYYMMDD as YYYY-MM-DD."""
    try:
        return datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return d


def classify_group(group: List[str]) -> str:
    """
    Return a classification string for the group:
    - 'exact' if all normalise to the same string
    - 'prefix' if prefix containment drives similarity
    - 'qualifier' if names differ only by qualifier words (flag separately)
    - 'fuzzy' for edit-distance / root matches
    """
    if len({normalise(n) for n in group}) == 1:
        return "exact"

    # Check if every pair differs by qualifiers
    qualifier_pairs = 0
    total_pairs = 0
    for i, a in enumerate(group):
        for b in group[i + 1:]:
            total_pairs += 1
            if has_qualifier_difference(tokenize(a), tokenize(b)):
                qualifier_pairs += 1

    if total_pairs > 0 and qualifier_pairs == total_pairs:
        return "qualifier"

    for i, a in enumerate(group):
        for b in group[i + 1:]:
            if prefix_match(a, b):
                return "prefix"

    return "fuzzy"


def group_note(classification: str) -> str:
    notes = {
        "exact": "These names normalise to the same string — safe to consolidate.",
        "prefix": "One name appears to be a prefix/subset of others — review whether the longer name is a distinct exercise.",
        "qualifier": "⚠️  Names differ only by equipment/grip qualifiers — **possible separate tracking intent**. Review carefully before merging.",
        "fuzzy": "Names share the same root or have high edit-distance similarity — possible typo or inconsistent naming.",
    }
    return notes.get(classification, "")


def render_report(
    groups: List[List[str]],
    stats: Dict[str, Dict],
    source_file: str,
) -> str:
    lines: List[str] = []
    lines.append("# Duplicate Exercise Name Candidates")
    lines.append("")
    lines.append(f"**Source file:** `{os.path.basename(source_file)}`  ")
    lines.append(f"**Total unique exercise names:** {len(stats)}  ")
    lines.append(f"**Candidate groups found:** {len(groups)}  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append("")
    lines.append(
        "> This report is for **human review only**. No data has been modified."
    )
    lines.append(
        "> Each group lists names that may refer to the same exercise."
    )
    lines.append(
        "> Groups marked ⚠️  differ by equipment/grip qualifiers and may be intentional distinct exercises."
    )
    lines.append("")

    # Sort groups: exact first, then prefix, then qualifier, then fuzzy
    # Within each type, sort by total appearances descending
    def sort_key(g: List[str]) -> Tuple:
        cls = classify_group(g)
        order = {"exact": 0, "prefix": 1, "fuzzy": 2, "qualifier": 3}
        total = sum(stats.get(n, {}).get("count", 0) for n in g)
        return (order.get(cls, 99), -total)

    groups_sorted = sorted(groups, key=sort_key)

    # Section headers
    sections: Dict[str, List[List[str]]] = {
        "exact": [],
        "prefix": [],
        "fuzzy": [],
        "qualifier": [],
    }
    for g in groups_sorted:
        sections[classify_group(g)].append(g)

    section_titles = {
        "exact": "## Exact Matches (after normalisation)",
        "prefix": "## Prefix / Subset Matches",
        "fuzzy": "## Fuzzy / Root Matches",
        "qualifier": "## Qualifier Differences (⚠️  Possible Separate Tracking Intent)",
    }

    for cls in ("exact", "prefix", "fuzzy", "qualifier"):
        grp_list = sections[cls]
        if not grp_list:
            continue
        lines.append(section_titles[cls])
        lines.append("")
        lines.append(f"*{group_note(cls)}*")
        lines.append("")

        for idx, group in enumerate(grp_list, 1):
            total_count = sum(stats.get(n, {}).get("count", 0) for n in group)
            lines.append(f"### Group {cls[0].upper()}{idx} — {total_count} total appearances")
            lines.append("")
            lines.append("| Exercise Name | Count | First Seen | Last Seen |")
            lines.append("|---|---|---|---|")
            for name in group:
                s = stats.get(name, {"count": 0, "dates": []})
                count = s["count"]
                dates = sorted(s["dates"])
                first = format_date(dates[0]) if dates else "—"
                last = format_date(dates[-1]) if dates else "—"
                lines.append(f"| `{name}` | {count} | {first} | {last} |")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## How to Use This Report")
    lines.append("")
    lines.append(
        "1. **Exact matches**: These are the lowest-hanging fruit — safe to consolidate in your JSON."
    )
    lines.append(
        "2. **Prefix matches**: Check whether the shorter name is a general category or a specific exercise."
    )
    lines.append(
        "3. **Fuzzy matches**: These may be typos or genuinely different exercises with similar names."
    )
    lines.append(
        "4. **Qualifier differences** (⚠️ ): These require the most care — different equipment or grip often means different muscle activation and separate progress tracking is valuable."
    )
    lines.append("")
    lines.append(
        "Re-run this script after any consolidation: `python scripts/find_duplicate_exercises.py`"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    default_output = os.path.join(
        project_root,
        ".agents",
        "checkpoints",
        "consolidate-duplicate-exercises",
        "report.md",
    )

    parser = argparse.ArgumentParser(
        description="Find potentially duplicate exercise names in workout JSON files."
    )
    parser.add_argument(
        "--input",
        metavar="PATH",
        default=None,
        help="Path to workout JSON file (default: auto-detect largest workouts_start_*.json)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=default_output,
        help=f"Path for the Markdown report (default: {default_output})",
    )
    parser.add_argument(
        "--threshold",
        metavar="FLOAT",
        type=float,
        default=0.82,
        help="Edit-distance similarity threshold 0.0–1.0 (default: 0.82)",
    )
    args = parser.parse_args()

    # Resolve input file
    if args.input:
        input_path = os.path.abspath(args.input)
    else:
        input_path = find_latest_workout_file(project_root)
    print(f"Reading: {input_path}", file=sys.stderr)

    # Load stats
    stats = load_exercise_stats(input_path)
    print(f"Unique exercise names: {len(stats)}", file=sys.stderr)

    # Build groups
    names = list(stats.keys())
    print("Computing similarity groups (may take a moment)...", file=sys.stderr)
    groups = build_similarity_groups(names)
    print(f"Candidate groups found: {len(groups)}", file=sys.stderr)

    # Render report
    report = render_report(groups, stats, input_path)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        f.write(report)
    print(f"Report written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
