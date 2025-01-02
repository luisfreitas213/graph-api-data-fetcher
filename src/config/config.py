import os

#URL
URL_BASE: str = "https://graph.facebook.com/v21.0/"
#PAGE METRICS ENDPOITNS
PAGE_ENDPOINT_BASE: str = f"{os.getenv("PAGE_ID")}"
PAGE_METRICS_ENDPOINT_BASE: str = f"{PAGE_ENDPOINT_BASE}/insights"
PAGE_METRICS: str = 'page_total_actions, page_post_engagements,page_fan_adds_by_paid_non_paid_unique, page_lifetime_engaged_followers_unique, page_daily_follows, page_daily_follows_unique, page_daily_unfollows_unique, page_follows, page_impressions, page_impressions_unique, page_impressions_paid, page_impressions_paid_unique, page_impressions_viral, page_impressions_viral_unique, page_impressions_nonviral, page_impressions_nonviral_unique, page_posts_impressions'
#POSTS ENDPOINTS
POST_ENDPOINT_BASE: str = f"{os.getenv("PAGE_ID")}/feed"
POST_METRICS: str = "post_reactions_like_total, post_reactions_love_total, post_reactions_wow_total, post_reactions_haha_total, post_reactions_sorry_total, post_reactions_anger_total, post_clicks, post_clicks_by_type, post_impressions, post_impressions_unique, post_impressions_paid, post_impressions_paid_unique, post_impressions_fan, post_impressions_fan_unique, post_impressions_organic, post_impressions_organic_unique, post_impressions_viral, post_impressions_viral_unique, post_impressions_nonviral, post_impressions_nonviral_unique"
#PATHS
OUTPUT_PATH: str = f"/datalake/raw/graph/{os.getenv("PAGE_NAME")}"
