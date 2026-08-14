import time
import requests
import feedparser

# ==========================================
# 1. YOUR FEED & WEBHOOK CONFIGURATION
# ==========================================

# Paste your RSS.app feed link inside the quotes below:
RSS_FEED_URL = "https://rss.app/feeds/ZQDRbgReHLNKgNc5.xml"

# Paste your Discord Webhook URLs inside the quotes below:
MTG_WEBHOOK = "https://discordapp.com/api/webhooks/1537643698601590836/kEtQcDDwCMT2x4mO_tj62dARm8hs6tnDKPkyI50nIza6GthK-9iusBSn2fGP1uiJZSBO"
POKEMON_WEBHOOK = "https://discordapp.com/api/webhooks/1537643826603229254/4aXufRaU_A7TyByXXjOFgcad8M5jAjJSeh-23-ozCMIp4JCkfGFzb-kwM4vCeXxIb9AM"
GENERAL_WEBHOOK = "https://discordapp.com/api/webhooks/1537646292975616070/y6xxRVdIkRMXNvZnCpkHhv_8jXfzHRHSl3xXvC3SJklBPIBJmaNr8EO0pyW71Ac1kJUN"  # Optional: for unmatched posts (or set to None)

# Keyword Mapping (Add or edit topics easily in the future)
ROUTES = [
    {
        "keywords": ["magic", "mtg", "commander", "draft", "prerelease", "lorcana"],  # Matches MTG or Lorcana
        "webhook": MTG_WEBHOOK
    },
    {
        "keywords": ["pokemon", "pokémon", "pikachu", "tcg", "booster"],
        "webhook": POKEMON_WEBHOOK
    }
]

CHECK_INTERVAL = 600  # Check for new posts every 10 minutes (600 seconds)

# Track processed post IDs to prevent duplicates
seen_posts = set()

def determine_webhook(content):
    """Scan post text against keywords to pick the right webhook."""
    content_lower = content.lower()
    
    for route in ROUTES:
        for keyword in route["keywords"]:
            if keyword in content_lower:
                return route["webhook"]
                
    # Fallback if no keywords match
    return GENERAL_WEBHOOK

def check_facebook_feed():
    print("Checking Facebook RSS feed for new posts...")
    feed = feedparser.parse(RSS_FEED_URL)
    
    # Process oldest fresh post first
    for entry in reversed(feed.entries):
        post_id = entry.id if 'id' in entry else entry.link
        
        if post_id not in seen_posts:
            # Combine title and summary/description to capture all keywords
            post_title = getattr(entry, 'title', '')
            post_summary = getattr(entry, 'summary', '')
            full_text = f"{post_title} {post_summary}"
            
            # Select target channel based on keywords
            target_webhook = determine_webhook(full_text)
            
            if target_webhook:
                payload = {
                    "content": f"📢 **New Post Alert!**\n\n{entry.title}\n\n🔗 {entry.link}"
                }
                
                response = requests.post(target_webhook, json=payload)
                if response.status_code in [200, 204]:
                    print(f"✅ Successfully routed post to Discord: {entry.title[:30]}...")
                    seen_posts.add(post_id)
                else:
                    print(f"❌ Failed to send to Discord (Status {response.status_code})")
            else:
                # If no webhook matches and GENERAL_WEBHOOK is None/empty, skip it
                print(f"ℹ️ Skipping post (no matching keywords found): {entry.title[:30]}...")
                seen_posts.add(post_id)

# ==========================================
# 2. SCRIPT RUNNER
# ==========================================

if __name__ == "__main__":
    # Populate initial posts so the bot doesn't spam old posts on start
    initial_feed = feedparser.parse(RSS_FEED_URL)
    for entry in initial_feed.entries:
        seen_posts.add(entry.id if 'id' in entry else entry.link)
        
    print("🚀 Bot started! Monitoring feed with keyword routing...")
    
    while True:
        try:
            check_facebook_feed()
        except Exception as e:
            print(f"⚠️ Error encountered during check: {e}")
        
        time.sleep(CHECK_INTERVAL)