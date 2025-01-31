from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_last_30_days_intervals():
    """
    Generate a list of dictionaries with the intervals for the last 30 days, excluding today.

    Returns:
        list: List of dictionaries containing 'since' and 'until' dates.
    """
    today = datetime.today()
    intervals = []

    for i in range(1, 1):  # Start from yesterday (1) to 30 days ago
        since_date = today - timedelta(days=i+1)
        until_date = today - timedelta(days=i)

        intervals.append({
            "since": since_date.strftime("%Y-%m-%d"),
            "until": until_date.strftime("%Y-%m-%d")
        })

    return intervals


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

def get_monthly_15_day_intervals(num_months: int):
    """
    Generate 15-day intervals for the last `num_months`, 
    aligned to days 1-15 and 16-last day of the month.
    Includes custom logic for the current month.

    Args:
        num_months (int): Number of months to calculate intervals for.

    Returns:
        list: List of 15-day intervals.
    """
    today = datetime.today()
    intervals = []

    for i in range(0, int(num_months) + 1):
        end_date = today.replace(day=1) - relativedelta(months=i - 1)
        start_date_request_first = end_date - relativedelta(months=1) - relativedelta(days=1)
        start_date_request_second = (end_date - relativedelta(months=1)).replace(day=15)
        start_date_first = end_date - relativedelta(months=1)

        intervals.append( {
            "since": start_date_request_second.strftime("%Y-%m-%d"),
            "until": (end_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            "start_date": start_date_request_second.strftime("%Y-%m-%d")
        })

        intervals.append( {
            "since": start_date_request_first.strftime("%Y-%m-%d"),
            "until": (start_date_request_second).strftime("%Y-%m-%d"),
            "start_date": start_date_first.strftime("%Y-%m-%d")
        })



    return intervals
