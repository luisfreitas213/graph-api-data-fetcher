import json
import os
from config.config import OUTPUT_PATH, PAGE_ENDPOINT_BASE, PAGE_METRICS, PAGE_METRICS_ENDPOINT_BASE, POST_ENDPOINT_BASE, POST_METRICS
from extract.api_client import GraphAPIClient
from utils.utils import get_last_months_intervals,get_monthly_15_day_intervals

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
    for interval in intervals_date:
        # PAGE METRICS
        # Construct request parameters
        params = {
            'metric': PAGE_METRICS,
            'since': str(interval["since"]),
            'until': str(interval["until"]),
            'period': 'day'  # Daily aggregation
        }

        # Define output directory and file name
        output_dir = os.path.join(OUTPUT_PATH, "facebook_page_metrics")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        file_name = f"{interval['start_date']}_{interval['until']}.json"

        # Fetch and save data
        client.fetch_data(
            params=params,
            output_dir=output_dir,
            endpoint=PAGE_METRICS_ENDPOINT_BASE,
            file_name=file_name
            )
        # POSTS
        # Construct request parameters
        params = {
            "fields": "id,message,created_time,attachments{media_type,media,url}",
            'since': str(interval["since"]),
            'until': str(interval["until"])
        }

        # Define output directory and file name
        output_dir = os.path.join(OUTPUT_PATH, "facebook_posts")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        file_name = f"{interval['start_date']}_{interval['until']}.json"

        # Fetch and save data
        client.fetch_data(
            params=params,
            output_dir=output_dir,
            endpoint=POST_ENDPOINT_BASE,
            file_name=file_name
        )
        #POST METRICS
        file_path = os.path.join(output_dir, file_name)
        # Read the file and loop through each post
        with open(file_path, "r", encoding="utf-8") as file:
            posts_data = json.load(file)
            for post in posts_data["data"]:
                post_id = str(post["id"])
                # Construct request parameters
                params = {
                    "metric": POST_METRICS
                }

                # Define output directory and file name
                output_dir = os.path.join(OUTPUT_PATH, "facebook_post_metrics")
                os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

                file_name = f"{post_id}.json"
                # Fetch and save data
                client.fetch_data(
                    params=params,
                    output_dir=output_dir,
                    endpoint= f"{post_id}/insights",
                    file_name=file_name
                )

    #Get Instagram Business Account
    params = {
    "fields": "instagram_business_account",
    }
    output_dir = os.path.join(OUTPUT_PATH, "instagram_business_account")
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    file_name = "instagram_business_account.json"
    client.fetch_data(
        params=params,
        output_dir=output_dir,
        endpoint=PAGE_ENDPOINT_BASE,
        file_name=file_name,
        extend_data = False
    )

    file_path = os.path.join(output_dir, file_name)
    # Read the file and loop through each post
    with open(file_path, "r", encoding="utf-8") as file:
        ig_account  = json.load(file)["data"]["instagram_business_account"]["id"]

    # Get date intervals for data extraction
    try:
        num_months = int(os.getenv("NUM_MONTHS_DATA", "1"))  # Default to 1 month if not set
        intervals_date = get_monthly_15_day_intervals(
            num_months=num_months)
    except ValueError as e:
        raise ValueError("NUM_MONTHS_DATA must be an integer.") from e

    # Iterate over metrics and date intervals to fetch data
    for interval in intervals_date:
        # Instagram profile Metrics
        params = {
            "metric": "impressions,reach",
            'since': str(interval["since"]),
            'until': str(interval["until"]),
            "period": "day"
        }

        # Define output directory and file name
        output_dir = os.path.join(OUTPUT_PATH, "instagram_page_metrics")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        file_name = f"{interval['start_date']}_{interval['until']}.json"

        # Fetch and save data
        client.fetch_data(
            params=params,
            output_dir=output_dir,
            endpoint=f"{ig_account}/insights",
            file_name=file_name
            )

    print("ETL process completed successfully.")
