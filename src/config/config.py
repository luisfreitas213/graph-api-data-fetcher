import os
from pathlib import Path

# Environment Variables with Defaults
PAGE_ID = os.getenv("PAGE_ID", "")
PAGE_NAME = os.getenv("PAGE_NAME", "default_page")
ADS_ACCOUNT = os.getenv("ADS_ACCOUNT", "")

# Base URLs
URL_BASE = "https://graph.facebook.com/v22.0/"

# Page Metrics
PAGE_ENDPOINT_BASE = f"{PAGE_ID}"
PAGE_METRICS_ENDPOINT_BASE = f"{PAGE_ID}/insights"
PAGE_METRICS = ",".join([
    "page_total_actions", "page_post_engagements", "page_fan_adds_by_paid_non_paid_unique",
    "page_lifetime_engaged_followers_unique", "page_daily_follows", "page_daily_follows_unique",
    "page_daily_unfollows_unique", "page_follows", "page_impressions", "page_impressions_unique",
    "page_impressions_paid", "page_impressions_paid_unique", "page_impressions_viral",
    "page_impressions_viral_unique", "page_impressions_nonviral", "page_impressions_nonviral_unique",
    "page_posts_impressions"
])

# Post Metrics
POST_ENDPOINT_BASE = f"{PAGE_ID}/feed"
POST_METRICS = ",".join([
    "post_reactions_like_total", "post_reactions_love_total", "post_reactions_wow_total",
    "post_reactions_haha_total", "post_reactions_sorry_total", "post_reactions_anger_total",
    "post_clicks", "post_clicks_by_type", "post_impressions", "post_impressions_unique",
    "post_impressions_paid", "post_impressions_paid_unique", "post_impressions_fan",
    "post_impressions_fan_unique", "post_impressions_organic", "post_impressions_organic_unique",
    "post_impressions_viral", "post_impressions_viral_unique", "post_impressions_nonviral",
    "post_impressions_nonviral_unique"
])

# Instagram Metrics
INSTA_PAGE_METRICS = ",".join([
    "reach", "accounts_engaged", "likes", "comments", "shares", "saves", "replies",
    "follows_and_unfollows", "profile_links_taps", "follower_count"
])

INSTA_POST_METRICS = ",".join([
    "comments", "follows", "likes", "profile_activity", "profile_visits", "reach",
    "saved", "shares", "total_interactions", "views"
])

INSTA_REEL_METRICS = ",".join([
    "comments", "likes", "reach", "saved", "shares", "total_interactions", "views",
    "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"
])

# Output Paths (Using Pathlib)
OUTPUT_PATH = Path(f"/datalake/raw/graph/{PAGE_NAME}")

# Ads Account
ADS_ACCOUNT = f"{ADS_ACCOUNT}"

# Security
TOKEN_FILE = Path(f"/datalake/raw/graph/{PAGE_NAME}/security/secure_token.json")
ENCRYPTION_KEY_FILE = Path(f"/datalake/raw/graph/{PAGE_NAME}/security/key.key")
