#!/usr/bin/env python3
"""Translate related-services.json to English."""
import io

FP = "/Users/maabook/Desktop/beriklan.my/web/src/data/related-services.json"

CONTENT = '''{
    "schema_version": "1.0",
    "last_updated": "2026-07-21",
    "description": "Internal linking matrix for RelatedServices component. Each main service has 3 strongly-related services. City pages use parent service's matrix.",

    "services": {
        "facebook-ads-management": [
            { "slug": "instagram-ads-management", "label": "Instagram Ads", "icon": "\\ud83d\\udcf7", "desc": "Visual storytelling to reach new audiences across Feed, Stories and Reels." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Reach younger audiences with short-form video that entertains and converts." },
            { "slug": "google-ads-management", "label": "Google Search Ads", "icon": "\\ud83d\\udd0d", "desc": "Capture high intent from people actively searching for your product or service." }
        ],
        "instagram-ads-management": [
            { "slug": "facebook-ads-management", "label": "Facebook Ads", "icon": "\\ud83d\\udcd8", "desc": "Same Meta Ads Manager. Ideal to manage alongside Instagram." },
            { "slug": "instagram-management", "label": "Instagram Management", "icon": "\\ud83d\\udcf1", "desc": "Organic content & community management for your IG account." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Add a short-video channel to fill the top of your funnel." }
        ],
        "tiktok-ads-management": [
            { "slug": "tiktok-management", "label": "TikTok Management", "icon": "\\ud83d\\udcf1", "desc": "Consistent organic TikTok content, aligned with your paid ads." },
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Boost viewers during TikTok live streams to trigger the algorithm faster." },
            { "slug": "instagram-ads-management", "label": "Instagram Ads", "icon": "\\ud83d\\udcf7", "desc": "Cross-channel: reach IG with content repurposed from TikTok." }
        ],
        "google-ads-management": [
            { "slug": "youtube-ads-management", "label": "YouTube Ads", "icon": "\\u25b6\\ufe0f", "desc": "Reach audiences via video on YouTube through the Google Ads network." },
            { "slug": "website-development", "label": "Website Development", "icon": "\\ud83d\\udcbb", "desc": "A stronger landing destination for your Google Ads traffic." },
            { "slug": "landing-page-design", "label": "Landing Page Design", "icon": "\\ud83c\\udfaf", "desc": "High-converting LPs designed specifically for Google Ads campaigns." }
        ],
        "youtube-ads-management": [
            { "slug": "google-ads-management", "label": "Google Ads", "icon": "\\ud83d\\udd0d", "desc": "YouTube Ads is part of the Google Ads network. Managing both together is more efficient." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Short-form video ads. Great for running the same brand in multiple formats." },
            { "slug": "youtube-live-viewers", "label": "YouTube Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Boost YouTube Live viewers to trend faster." }
        ],
        "instagram-management": [
            { "slug": "instagram-ads-management", "label": "Instagram Ads", "icon": "\\ud83d\\udcf7", "desc": "Paid ads for scaling; organic management for nurture." },
            { "slug": "facebook-ads-management", "label": "Facebook Ads", "icon": "\\ud83d\\udcd8", "desc": "Across the Meta platform. One Ads Manager strategy for IG & FB." },
            { "slug": "tiktok-management", "label": "TikTok Management", "icon": "\\ud83d\\udcf1", "desc": "Organic TikTok as an amplifier for your IG content." }
        ],
        "tiktok-management": [
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Boost your best organic content with paid ads to scale." },
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "During lives, viewers trigger the algorithm. Boost them for growth." },
            { "slug": "instagram-ads-management", "label": "Instagram Ads", "icon": "\\ud83d\\udcf7", "desc": "Repurpose TikTok content for IG; add a paid boost for reach." }
        ],
        "website-development": [
            { "slug": "landing-page-design", "label": "Landing Page Design", "icon": "\\ud83c\\udfaf", "desc": "LPs for specific campaigns — design & copy tuned for conversion." },
            { "slug": "google-ads-management", "label": "Google Ads", "icon": "\\ud83d\\udd0d", "desc": "Drive Google Search Ads traffic to your new SEO-ready website." },
            { "slug": "digital-marketing-agency", "label": "Digital Marketing", "icon": "\\ud83d\\udcc8", "desc": "Once your website is live, full-funnel marketing drives growth." }
        ],
        "landing-page-design": [
            { "slug": "google-ads-management", "label": "Google Ads", "icon": "\\ud83d\\udd0d", "desc": "Landing Page + Google Ads: a conversion bundle that works hand in hand." },
            { "slug": "facebook-ads-management", "label": "Facebook Ads", "icon": "\\ud83d\\udcd8", "desc": "FB Ads traffic to an LP already tuned for the Meta pixel." },
            { "slug": "website-development", "label": "Website Development", "icon": "\\ud83d\\udcbb", "desc": "Build your main brand on a website, then use LPs for specific campaigns." }
        ],
        "digital-marketing-agency": [
            { "slug": "facebook-ads-management", "label": "Facebook Ads", "icon": "\\ud83d\\udcd8", "desc": "The core channel for B2C, lead gen and brand awareness." },
            { "slug": "google-ads-management", "label": "Google Ads", "icon": "\\ud83d\\udd0d", "desc": "Capture high-intent search traffic that is ready to convert." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Reach younger audiences plus FYP viral potential." }
        ],
        "live-stream-viewers": [
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Boost TikTok Live viewers to trend." },
            { "slug": "instagram-live-viewers", "label": "Instagram Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Boost viewers during IG Live selling sessions or product launches." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "After the live, follow up with paid ads to scale." }
        ],
        "tiktok-live-viewers": [
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Paid ads + boosted live viewers = faster scaling." },
            { "slug": "shopee-live-viewers", "label": "Shopee Live Viewers", "icon": "\\ud83d\\uded2", "desc": "Cross-platform: TikTok \\u2192 Shopee Live for e-commerce." },
            { "slug": "instagram-live-viewers", "label": "Instagram Live Viewers", "icon": "\\ud83d\\udcf7", "desc": "Multi-channel live strategy." }
        ],
        "instagram-live-viewers": [
            { "slug": "instagram-ads-management", "label": "Instagram Ads", "icon": "\\ud83d\\udcf7", "desc": "Paid boosting for post-live content." },
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Cross-platform: IG + TikTok Live at the same time." },
            { "slug": "instagram-management", "label": "Instagram Management", "icon": "\\ud83d\\udcf1", "desc": "Organic + live boosts for a full funnel." }
        ],
        "shopee-live-viewers": [
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Many shoppers move from TikTok Live to Shopee during flash sales." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Drive traffic to your Shopee Live via TikTok ads." },
            { "slug": "instagram-live-viewers", "label": "Instagram Live Viewers", "icon": "\\ud83d\\udcf7", "desc": "Multi-platform Shopee + IG boosts." }
        ],
        "youtube-live-viewers": [
            { "slug": "youtube-ads-management", "label": "YouTube Ads", "icon": "\\u25b6\\ufe0f", "desc": "Pre-recorded ads + live = a full YouTube funnel." },
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Cross-platform: YouTube + TikTok Live." },
            { "slug": "twitch-live-viewers", "label": "Twitch Live Viewers", "icon": "\\ud83c\\udfae", "desc": "Gaming/community live boost." }
        ],
        "twitch-live-viewers": [
            { "slug": "youtube-live-viewers", "label": "YouTube Live Viewers", "icon": "\\ud83d\\udd34", "desc": "Cross-platform live: Twitch + YouTube." },
            { "slug": "tiktok-live-viewers", "label": "TikTok Live Viewers", "icon": "\\ud83c\\udfb4", "desc": "Twitch audience \\u2192 TikTok growth." },
            { "slug": "tiktok-ads-management", "label": "TikTok Ads", "icon": "\\ud83c\\udfb5", "desc": "Twitch + TikTok ads = gaming/esports exposure." }
        ]
    },

    "city_pages_alias": "_use_parent_service_"
}
'''

# Validate JSON before writing
import json
json.loads(CONTENT)

with io.open(FP, 'w', encoding='utf-8') as f:
    f.write(CONTENT)
print('WROTE related-services.json (English)')
