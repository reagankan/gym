import numpy as np
from collections import defaultdict

def remove_outliers(exercise_data, k=1.5, min_points=3):
    """
    Removes outliers per exercise using all weights across all dates.

    Args:
        exercise_data: dict[exercise][date] -> list[weights]
        k: IQR multiplier
        min_points: minimum total points to apply filtering

    Returns:
        cleaned exercise_data with same structure
    """

    cleaned = defaultdict(lambda: defaultdict(list))

    for exercise, date_map in exercise_data.items():
        # flatten all weights for this exercise
        all_weights = [
            w for weights in date_map.values() for w in weights
        ]

        if len(all_weights) < min_points:
            cleaned[exercise] = date_map
            continue

        arr = np.array(all_weights)
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1

        # print(f"q1: {q1}")
        # print(f"q3: {q3}")
        # print(f"iqr: {iqr}")

        if iqr == 0:
            cleaned[exercise] = date_map
            continue

        low = q1 - k * iqr
        high = q3 + k * iqr

        for date, weights in date_map.items():
            filtered = [
                w for w in weights if low <= w <= high
            ]
            cleaned[exercise][date] = filtered

    return cleaned

    
