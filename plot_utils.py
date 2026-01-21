import matplotlib.pyplot as plt

def plot_years(dates):
    
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


def plot_exercise_boxplot(exercise_name, exercise_data):
    """
    exercise_data: dict[date] -> list[weights]
    """

    dates = sorted(exercise_data.keys())
    weights = [exercise_data[d] for d in dates]

    if not weights:
        return

    plt.figure(figsize=(8, 4))

    plt.boxplot(weights, labels=dates, showfliers=False)
    plot_years(dates)

    plt.title(exercise_name)
    plt.xlabel("Date")
    plt.ylabel("Weight (lbs)")

    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()
