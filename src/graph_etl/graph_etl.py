import json
import os
from config.config import ADS_ACCOUNT, INSTA_PAGE_METRICS, INSTA_POST_METRICS, INSTA_REEL_METRICS, OUTPUT_PATH, PAGE_ENDPOINT_BASE, PAGE_METRICS, PAGE_METRICS_ENDPOINT_BASE, POST_ENDPOINT_BASE, POST_METRICS
from extract.api_client import GraphAPIClient
from utils.utils import  get_last_months_intervals

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

    #Get Instagram Media
    params = {
    "fields": "id,caption,media_type,media_url,timestamp,permalink"
    }
    file_name = "instagram_media.json"
    output_dir = os.path.join(OUTPUT_PATH, "instagram_media")
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    client.fetch_data(
        params=params,
        output_dir=output_dir,
        endpoint=f"{ig_account}/media",
        file_name=file_name
    )

    file_path = os.path.join(output_dir, file_name)
    # Step 1: Read Media IDs from File
    with open(file_path, "r", encoding="utf-8") as file:
        media_ids = json.load(file)

    # Step 2: Fetch Metrics for Each Media ID
    for media_item in media_ids["data"]:
        media_id = media_item["id"]
        media_type = media_item["media_type"]
        file_name = f"{media_id}.json"
        if media_type == "VIDEO":
            output_dir = os.path.join(OUTPUT_PATH, "insta_reels_metrics")
            params = {
                "metric": INSTA_REEL_METRICS
            }
            client.fetch_data(
                params=params,
                output_dir=output_dir,
                endpoint=f"{media_id}/insights",
                file_name=file_name
            )
        else:
            output_dir = os.path.join(OUTPUT_PATH, "insta_posts_metrics")
            params = {
                "metric": INSTA_POST_METRICS
            }
            client.fetch_data(
                params=params,
                output_dir=output_dir,
                endpoint=f"{media_id}/insights",
                file_name=file_name
            )

    ### **4. FETCH ADS & METRICS**
    # **Step 1: Fetch Campaigns**
    params = {
        "fields": "id,name,objective,status",
        "limit": 100
    }

    campaigns_output_dir = os.path.join(OUTPUT_PATH, "campaigns")
    os.makedirs(campaigns_output_dir, exist_ok=True)

    file_name = "campaigns_list.json"
    client.fetch_data(
        params=params,
        output_dir=campaigns_output_dir,
        endpoint=f"act_{ADS_ACCOUNT}/campaigns",
        file_name=file_name,
        page=False
    )

    # **Step 2: Fetch Ad Sets**
    params = {
        "fields": "id,name,campaign_id,targeting,budget,status",
        "limit": 100
    }

    adsets_output_dir = os.path.join(OUTPUT_PATH, "adsets")
    os.makedirs(adsets_output_dir, exist_ok=True)

    file_name = "adsets_list.json"
    client.fetch_data(
        params=params,
        output_dir=adsets_output_dir,
        endpoint=f"act_{ADS_ACCOUNT}/adsets",
        file_name=file_name,
        page=False
    )

    # **Step 3: Fetch Ads with Campaign & Ad Set**
    params = {
        "fields": "id,name,creative{id},campaign_id,adset_id,status",
        "limit": 100
    }

    ads_output_dir = os.path.join(OUTPUT_PATH, "ads")
    os.makedirs(ads_output_dir, exist_ok=True)

    file_name = "ads_list.json"
    client.fetch_data(
        params=params,
        output_dir=ads_output_dir,
        endpoint=f"act_{ADS_ACCOUNT}/ads",
        file_name=file_name,
        page=False
    )

    # **Step 4: Fetch Insights for Campaigns & Ad Sets**
    # Fetch insights per month
    for interval in intervals_date:

        # **Step 4.1: Fetch Campaign Insights**
        file_path = os.path.join(campaigns_output_dir, "campaigns_list.json")
        with open(file_path, "r", encoding="utf-8") as file:
            campaigns_data = json.load(file)

        for campaign in campaigns_data["data"]:
            campaign_id = campaign["id"]
            file_name = f"{campaign_id}_{interval['since']}_to_{interval['until']}.json"

            params = {
                "fields": "spend,clicks,impressions,reach,ctr,cpc",
                "time_range": json.dumps({
                    "since": interval["since"],
                    "until": interval["until"]
                }),
                "time_increment": "monthly"
            }

            campaign_insights_output_dir = os.path.join(OUTPUT_PATH, "campaigns_insights")
            os.makedirs(campaign_insights_output_dir, exist_ok=True)

            client.fetch_data(
                params=params,
                output_dir=campaign_insights_output_dir,
                endpoint=f"{campaign_id}/insights",
                file_name=file_name,
                page=False
            )

        # **Step 4.2: Fetch Ad Set Insights**
        file_path = os.path.join(adsets_output_dir, "adsets_list.json")
        with open(file_path, "r", encoding="utf-8") as file:
            adsets_data = json.load(file)

        for adset in adsets_data["data"]:
            adset_id = adset["id"]
            file_name = f"{adset_id}_{interval['since']}_to_{interval['until']}.json"

            params = {
                "fields": "spend,clicks,impressions,reach,ctr,cpc",
                "time_range": json.dumps({
                    "since": interval["since"],
                    "until": interval["until"]
                }),
                "time_increment": "monthly"
            }

            adset_insights_output_dir = os.path.join(OUTPUT_PATH, "adsets_insights")
            os.makedirs(adset_insights_output_dir, exist_ok=True)

            client.fetch_data(
                params=params,
                output_dir=adset_insights_output_dir,
                endpoint=f"{adset_id}/insights",
                file_name=file_name,
                page=False
            )

        # **Step 4.3: Fetch Ads Set Insights**
        file_path = os.path.join(ads_output_dir, "ads_list.json")
        with open(file_path, "r", encoding="utf-8") as file:
            ads_data = json.load(file)

        for ad in ads_data["data"]:
            ad_id = ad["id"]
            creative_id = ad.get("creative", {}).get("id")
            file_name = f"{ad_id}_{interval['since']}_to_{interval['until']}.json"

            # Fetch Ad Insights per month
            params = {
                "fields": "spend,clicks,impressions,reach,ctr,cpc",
                "time_range": json.dumps({
                    "since": interval["since"],
                    "until": interval["until"]
                }),
                "time_increment": "monthly"
            }

            output_dir = os.path.join(OUTPUT_PATH, "ads_insights")
            client.fetch_data(
                params=params,
                output_dir=output_dir,
                endpoint=f"{ad_id}/insights",
                file_name=file_name,
                page=False
            )

            # # **Step 4.4: Fetch Creative Details
            if creative_id:
                params = {
                    "fields": "object_story_id,thumbnail_url,title,body,image_url"
                }

                output_dir = os.path.join(OUTPUT_PATH, "ads_creatives")
                file_name = f"{creative_id}.json"

                client.fetch_data(
                    params=params,
                    output_dir=output_dir,
                    endpoint=f"{creative_id}",
                    file_name=file_name,
                    page=False,
                    extend_data = False
                )


    print("ETL process completed successfully.")
