from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_last_months_intervals(num_months: int):
    """
    Generate a dictionary with the intervals for the last `num_months`.

    Args:
        num_months (int): Number of months to generate intervals for.

    Returns:
        dict: Dictionary of intervals for the last `num_months`.
    """
    today = datetime.today()
    intervals = []

    for i in range(0, int(num_months) + 1):
        end_date = today.replace(day=1) - relativedelta(months=i - 1)
        start_date_request = end_date - relativedelta(months=1) - relativedelta(days=1)
        start_date = end_date - relativedelta(months=1)

        intervals.append( {
            "since": start_date_request.strftime("%Y-%m-%d"),
            "until": (end_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            "start_date": start_date.strftime("%Y-%m-%d")
        })

    return intervals
