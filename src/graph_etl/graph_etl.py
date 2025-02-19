from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from config.config import (
    ADS_ACCOUNT, INSTA_PAGE_METRICS, INSTA_POST_METRICS, INSTA_REEL_METRICS, OUTPUT_PATH, 
    PAGE_ENDPOINT_BASE, PAGE_METRICS, PAGE_METRICS_ENDPOINT_BASE, POST_ENDPOINT_BASE, POST_METRICS
)
from extract.api_client import GraphAPIClient
from utils.utils import get_last_months_intervals

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def ensure_directory(path: str) -> Path:
    """Ensure a directory exists and return the path.

    Args:
        path (str): Directory path.

    Returns:
        Path: Ensured directory path.
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def fetch_and_save(client: GraphAPIClient,
                    params: Dict[str, str],
                      endpoint: str,
                        output_dir: str,
                          file_name: str,
                            extend_data: bool = True,
                              page: bool = True) -> None:
    """Helper function to fetch data and save it to a file.

    Args:
        client (GraphAPIClient): The API client instance.
        params (Dict[str, str]): Request parameters.
        endpoint (str): API endpoint.
        output_dir (str): Output directory path.
        file_name (str): Name of the output file.
        extend_data (bool, optional): Whether to extend data in pagination. Defaults to True.
        page (bool, optional): Whether pagination is needed. Defaults to True.
    """
    output_path = ensure_directory(output_dir) / file_name
    client.fetch_data(
        params=params,
        output_dir=str(output_path.parent),
        endpoint=endpoint,
        file_name=file_name,
        extend_data=extend_data,
        page=page
    )


def load_json_file(file_path: str) -> Optional[Dict]:
    """Load a JSON file and return its contents.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Optional[Dict]: Parsed JSON data or None if error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None


def fetch_page_metrics(client: GraphAPIClient, intervals: List[Dict[str, str]]) -> None:
    """Fetch page-level metrics from the Facebook Graph API.

    Args:
        client (GraphAPIClient): The API client instance.
        intervals (List[Dict[str, str]]): List of date intervals.
    """
    for interval in intervals:
        fetch_and_save(
            client,
            params={
                'metric': PAGE_METRICS,
                  'since': interval["since"],
                    'until': interval["until"],
                     'period': 'day'},
            endpoint=PAGE_METRICS_ENDPOINT_BASE,
            output_dir=f"{OUTPUT_PATH}/facebook_page_metrics",
            file_name=f"{interval['start_date']}_{interval['until']}.json"
        )


def fetch_posts(client: GraphAPIClient, intervals: List[Dict[str, str]]) -> None:
    """Fetch posts from the Facebook page.

    Args:
        client (GraphAPIClient): The API client instance.
        intervals (List[Dict[str, str]]): List of date intervals.
    """
    for interval in intervals:
        fetch_and_save(
            client,
            params={"fields": "id,message,created_time,attachments{media_type,media,url}",
                    'since': interval["since"], 'until': interval["until"]},
            endpoint=POST_ENDPOINT_BASE,
            output_dir=f"{OUTPUT_PATH}/facebook_posts",
            file_name=f"{interval['start_date']}_{interval['until']}.json"
        )


def fetch_post_metrics(client: GraphAPIClient, intervals: List[Dict[str, str]]) -> None:
    """Fetch post-level metrics.

    Args:
        client (GraphAPIClient): The API client instance.
        intervals (List[Dict[str, str]]): List of date intervals.
    """
    for interval in intervals:
        posts_data = load_json_file(
            f"{OUTPUT_PATH}/facebook_posts/{interval['start_date']}_{interval['until']}.json")
        if posts_data:
            for post in posts_data.get("data", []):
                fetch_and_save(
                    client,
                    params={"metric": POST_METRICS},
                    endpoint=f"{post['id']}/insights",
                    output_dir=f"{OUTPUT_PATH}/facebook_post_metrics",
                    file_name=f"{post['id']}.json"
                )


def fetch_instagram_data(client: GraphAPIClient) -> None:
    """Fetch Instagram business account, media, and metrics.

    Args:
        client (GraphAPIClient): The API client instance.
    """
    fetch_and_save(
        client,
        params={"fields": "instagram_business_account"},
        endpoint=PAGE_ENDPOINT_BASE,
        output_dir=f"{OUTPUT_PATH}/instagram_business_account",
        file_name="instagram_business_account.json",
        extend_data=False
    )

    ig_account_data = load_json_file(
        f"{OUTPUT_PATH}/instagram_business_account/instagram_business_account.json")
    if not ig_account_data:
        return

    ig_account_id = ig_account_data.get("data", {}).get("instagram_business_account", {}).get("id")

    fetch_and_save(
        client,
        params={"fields": "id,caption,media_type,media_url,timestamp,permalink"},
        endpoint=f"{ig_account_id}/media",
        output_dir=f"{OUTPUT_PATH}/instagram_media",
        file_name="instagram_media.json"
    )


def fetch_facebook_ads(client: GraphAPIClient) -> None:
    """Fetch Facebook Ads campaign, ad sets, and ads.

    Args:
        client (GraphAPIClient): The API client instance.
    """
    ads_categories = {
        "campaigns": "id,name,objective,status",
        "adsets": "id,name,campaign_id,targeting,budget,status",
        "ads": "id,name,creative{id},campaign_id,adset_id,status"
    }

    for category, fields in ads_categories.items():
        fetch_and_save(
            client,
            params={"fields": fields, "limit": 100},
            endpoint=f"act_{ADS_ACCOUNT}/{category}",
            output_dir=f"{OUTPUT_PATH}/{category}",
            file_name=f"{category}_list.json",
            page=False
        )


def fetch_ads_insights_for_interval(client: GraphAPIClient, interval: Dict[str, str]) -> None:
    """Fetch insights for campaigns, ad sets, and ads for a specific interval.

    Args:
        client (GraphAPIClient): The API client instance.
        interval (Dict[str, str]): The date interval.
    """
    insights_fields = "spend,clicks,impressions,reach,ctr,cpc"

    for category in ["campaigns", "adsets", "ads"]:
        data = load_json_file(f"{OUTPUT_PATH}/{category}/{category}_list.json")
        if not data:
            continue

        for item in data.get("data", []):
            item_id = item["id"]
            fetch_and_save(
                client,
                params={
                    "fields": insights_fields,
                    "time_range": json.dumps(
                        {"since": interval["since"], "until": interval["until"]}),
                    "time_increment": "monthly"
                },
                endpoint=f"{item_id}/insights",
                output_dir=f"{OUTPUT_PATH}/{category}_insights",
                file_name=f"{item_id}_{interval['since']}_to_{interval['until']}.json",
                page=False
            )


def fetch_ads_insights_multithreaded(client: GraphAPIClient, intervals: List[Dict[str, str]]) -> None:
    """Fetch Ads insights in parallel for each interval.

    Args:
        client (GraphAPIClient): The API client instance.
        intervals (List[Dict[str, str]]): List of date intervals.
    """
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        future_to_interval = {
            executor.submit(fetch_ads_insights_for_interval, client, interval): interval
            for interval in intervals
        }

        for future in as_completed(future_to_interval):
            interval = future_to_interval[future]
            try:
                future.result()  # Get the result to catch exceptions
                logging.info(
                    f"Successfully fetched ads insights for interval: {interval['since']} to {interval['until']}")
            except Exception as e:
                logging.error(
                    f"Error fetching ads insights for interval {interval['since']} to {interval['until']}: {e}")


def etl() -> None:
    """Run the complete ETL process."""
    logging.info("Starting ETL process...")

    client = GraphAPIClient()
    num_months = int(os.getenv("NUM_MONTHS_DATA", "1"))
    intervals = get_last_months_intervals(num_months=num_months)

    etl_mode = os.getenv("ETL_MODE", "").lower()  # Get ETL mode

    if etl_mode == "social":
        logging.info("Running Social Media ETL...")
        fetch_page_metrics(client, intervals)
        fetch_posts(client, intervals)
        fetch_post_metrics(client, intervals)
        fetch_instagram_data(client)

    elif etl_mode == "ads":
        logging.info("Running Ads ETL...")
        fetch_facebook_ads(client)
        fetch_ads_insights_multithreaded(client, intervals)  # Run Ads insights in parallel

    else:
        logging.error('Invalid ETL_MODE. Set ETL_MODE to either "social" or "ads".')
        raise ValueError('Invalid ETL_MODE. Please set ETL_MODE to "social" or "ads".')

    logging.info("ETL process completed successfully.")


if __name__ == "__main__":
    etl()
