

def infer_workout_date_range(workouts):
    """
    Computes start_date, end_date, and number of dates from workouts list.
    
    workouts: list of parsed workouts, each starts with a date string "YYYYMMDD"
    
    Returns:
        start_date (str), end_date (str), num_dates (int)
    """
    if not workouts:
        return None, None, 0

    # Extract dates
    dates = [w[0] for w in workouts if w and isinstance(w[0], str)]

    # Sort dates ascending
    dates_sorted = sorted(dates)

    start_date = dates_sorted[0]
    end_date = dates_sorted[-1]
    num_dates = len(dates_sorted)

    return start_date, end_date, num_dates
