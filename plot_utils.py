import matplotlib.pyplot as plt

def annotate_years(dates):
    
    prev_year = None
    ymax = plt.ylim()[1]

    for i, d in enumerate(dates, start=1): # boxplot positions are 1-based
        year = d[:4]

        if prev_year is not None and year != prev_year:
            x = i - 0.5 # between years looks nicer

            # vertical line
            plt.axvline(
                x=x,
                linestyle="--",
                linewidth=1,
                alpha=0.5
            )

            # year label at top
            plt.text(
                x,
                ymax,
                year,
                ha="center",
                va="bottom",
                fontsize=9,
                alpha=0.7
            )

        prev_year = year

def get_personal_record(weights):
    if not weights:
        return None, None  # row_idx, max_value

    max_value = None
    max_row_idx = None

    for i, row in enumerate(weights):
        if not row:
            continue
        row_max = max(row)
        if (max_value is None) or (row_max > max_value):
            max_value = row_max
            max_row_idx = i

    return max_row_idx, max_value

def annotate_personal_record(weights):
    """
    Annotate the global max weight across all dates:
    - horizontal line at max weight
    - asterisk label at top (aligned with boxplot)
    """
    if not weights:
        return None

    max_row_idx, max_value = get_personal_record(weights)
    if max_value is None:
        return None

    # Horizontal PR line
    plt.axhline(
        y=max_value,
        linestyle="-",     # solid line
        linewidth=2,       # bold
        color="green",
    )

    ymax = plt.ylim()[0] # place at bottom of the graph to align with xticks.
    plt.text(
        max_row_idx + 1,  # boxplot positions are 1-based
        ymax,
        "*",
        ha="center",
        va="bottom",
        fontsize=24,          # make it chonky
        fontweight="bold",
        color="green",
        alpha=0.95
    )


def plot_exercise_boxplot(exercise_name, exercise_data):
    """
    exercise_data: dict[date] -> list[weights]
    """

    # sort things.
    dates = sorted(exercise_data.keys())
    weights = [exercise_data[d] for d in dates]
    print("exercise_data", exercise_data)

    if not weights:
        return None

    # size things.
    plt.figure(figsize=(8, 4))

    # plot things.
    plt.boxplot(weights, labels=dates, showfliers=True)
    annotate_years(dates)
    annotate_personal_record(weights)

    # label things.
    date_index, pr = get_personal_record(weights)
    plt.title(f"{exercise_name}\n{dates[date_index]}:{pr}")
    plt.xlabel("Date")
    plt.ylabel("Weight (lbs)")

    plt.xticks(rotation=45, ha='right', rotation_mode='anchor')

    plt.tight_layout()
    plt.show()
