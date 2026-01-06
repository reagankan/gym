import matplotlib.pyplot as plt

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
    plt.title(exercise_name)
    plt.xlabel("Date")
    plt.ylabel("Weight (lbs)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
