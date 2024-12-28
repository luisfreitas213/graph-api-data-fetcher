import os

#URL
URL_BASE: str = "https://graph.facebook.com/v21.0/"
#PAGE METRICS
PAGE_METRICS_ENDPOINT_BASE: str = f"{os.getenv("PAGE_ID")}/insights"
PAGE_METRICS_ENDPOINTS: list = ['page_views_total','page_impressions_unique']
#PATHS
OUTPUT_PATH: str = f"/datalake/raw/graph/{os.getenv("PAGE_NAME")}"
