import os
from config.config import OUTPUT_PATH, PAGE_METRICS_ENDPOINTS
from extract.api_client import GraphAPIClient
from utils.utils import get_last_months_intervals

def etl():
    """
    Extract, transform, and load data from the Graph API for given page metrics.
    Fetches daily aggregated data for each metric over a specified time interval.
    """

    # Initialize API client
    client = GraphAPIClient()

    # Get date intervals for data extraction
    try:
        num_months = int(os.getenv("NUM_MONTHS_DATA", "1"))  # Default to 1 month if not set
        intervals_date = get_last_months_intervals(num_months=num_months)
    except ValueError as e:
        raise ValueError("NUM_MONTHS_DATA must be an integer.") from e

    # Validate necessary environment variables
    page_id = os.getenv("PAGE_ID")
    if not page_id:
        raise EnvironmentError("PAGE_ID environment variable is not set.")

    # Iterate over metrics and date intervals to fetch data
    for page_metric in PAGE_METRICS_ENDPOINTS:
        for interval in intervals_date:

            # Construct request parameters
            params = {
                'metric': page_metric,
                'since': str(interval["since"]),
                'until': str(interval["until"]),
                'period': 'day'  # Daily aggregation
            }

            # Define output directory and file name
            output_dir = os.path.join(OUTPUT_PATH, page_metric)
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

            file_name = f"{interval['start_date']}_{interval['until']}.json"

            # Fetch and save data
            client.fetch_data(
                params=params,
                output_dir=output_dir,
                endpoint=f"/{page_id}/insights",
                file_name=file_name
            )

    print("ETL process completed successfully.")
