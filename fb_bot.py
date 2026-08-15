import os
import time
import threading
import requests
import feedparser
from flask import Flask

# ==========================================
# 1. YOUR FEED & WEBHOOK CONFIGURATION
# ==========================================

RSS_FEED_URL = "https://rss.app/feeds/ZQDRbgReHLNKgNc5.xml"

MTG_WEBHOOK = "https://discordapp.com/api/webhooks/1537969507316924549/4vs1U1A2gN4LmuKgU5PcsoI8s39LLSH_0yXNCkJ49_B8056BFCWiAy3eLAhLXubjGWIG"
POKEMON_WEBHOOK = "https://discordapp.com/api/webhooks/1537970832633102486/DtDJ2JzF1sMNN-uuunK9C9mM3NkXjIHfbdhP8b2t7YE_HmUGByh5xVKB5ykPTMMa7oas"
ELESTRALS_WEBHOOK = "https://discordapp.com/api/webhooks/1537971154587750450/no2J-GkzCD5tNIkvGhgaEchlIrXfJwhHS6qo77OX2WVvMNjcxaKyKuBn6cqhtXlp8W9h"
GUNDAM_WEBHOOK = "https://discordapp.com/api/webhooks/1537971417272950894/vKKxZnTtQnTiDE6uP0Nnfup_adhLa8RfsbOzoFL89Qz0vGC0XzITPBuLou2TkVVFrtoP"
OP_WEBHOOK = "https://discordapp.com/api/webhooks/1537971926553591928/FFsS1pe5vcwZ8uRKmX7KpRRSDPMJZhPSMj40cQNOFdPorVnhWGMH_QrmkFGIQ6xlXbWt"
COOKIERUN_WEBHOOK = "https://discordapp.com/api/webhooks/1537644174730469483/6S3G4hgixfMJm_wbZogKjNfjD6vysLyChJqUyFh6tCUX9zqqKwNeyE9IG2ZpUxm4SvJD"
RIFTBOUND_WEBHOOK = "https://discordapp.com/api/webhooks/1537981775446417409/_QBTVVDCYandDVQauShCHoOIV4GQ_Qej_Ce8arHMIHL30R7TvDUXA3P2ceGeIlH5Doqz"
GENERAL_WEBHOOK = "https://discordapp.com/api/webhooks/1537969840940122134/xSziXWUPn-oo1opMTpdyV8TjGeWbOnCFswNerjzqxCq-40TM21CQp1rMFBfZivVW79mS"

# ==========================================
# 2. KEYWORD ROUTING TABLE
# ==========================================

ROUTES = [
    {
        "name": "Magic: The Gathering",
        "keywords": [
            "magic", "mtg", "#mtg", "commander", "edh", "draft", 
            "modern", "pioneer", "standard", "wizards", "wotc", "secret lair", 
            "collector booster", "play booster", "mana", "planeswalker"
        ],
        "webhook": MTG_WEBHOOK
    },
    {
        "name": "Pokémon",
        "keywords": [
            "pokemon", "pokémon", "#pokemon", "pikachu", "charizard", "elite trainer box", 
            "etb", "booster bundle", "booster box", "scarlet", "violet", "sv0", 
            "trainer", "elite trainer", "prismatic", "stellar crown", "surging sparks", 
            "paldea", "pokemon tcg", "pokemontcg"
        ],
        "webhook": POKEMON_WEBHOOK
    },
    {
        "name": "Elestrals",
        "keywords": [
            "elestrals", "elestral", "#elestrals", "elestralstcg", "spirits", 
            "spirit deck", "clash", "runes", "caster", "shattered stars", 
            "frostfall", "daybreak", "stellar", "majestic rare", "adrive"
        ],
        "webhook": ELESTRALS_WEBHOOK
    },
    {
        "name": "Gundam Card Game",
        "keywords": [
            "gundam", "#gundam", "gunpla", "gundam tcg", "gundam card game", 
            "gcg", "mobile suit", "mobilesuit", "bandai", "bandai card games", 
            "newtype rising", "dual impact", "steel requiem", "phantom aria", 
            "freedom ascension", "gd01", "gd02", "gd03", "gd04", "gd05", "st01"
        ],
        "webhook": GUNDAM_WEBHOOK
    },
    {
        "name": "One Piece TCG",
        "keywords": [
            "one piece", "onepiece", "#onepiece", "#onepiecetcg", "optcg", "op tcg", 
            "luffy", "straw hat", "pirate", "bandai op", "op0", "op-", "op01", 
            "op02", "op03", "op04", "op05", "op06", "op07", "op08", "op09", "op10", 
            "devil fruit"
        ],
        "webhook": OP_WEBHOOK
    },
    {
        "name": "CookieRun: Braverse",
        "keywords": [
            "cookierun", "cookie run", "#cookierun", "#braverse", "braverse", 
            "cookieruntcg", "gingerbrave", "devsisters", "brave league", 
            "brave beginning", "cookie card", "battle area", "break area"
        ],
        "webhook": COOKIERUN_WEBHOOK
    },
    {
        "name": "Riftbound",
        "keywords": [
            "riftbound", "#riftbound", "riftboundtcg", "rift", "summoner", 
            "mana rift", "riftbound tcg"
        ],
        "webhook": RIFTBOUND_WEBHOOK
    }
]

CHECK_INTERVAL = 600  # 10 minutes
seen_posts = set()

# ==========================================
# 3. ROUTING & POSTING LOGIC
# ==========================================

def determine_webhook(content):
    content_lower = content.lower()
    for route in ROUTES:
        for keyword in route["keywords"]:
            if keyword in content_lower:
                return route["webhook"], route["name"]
    return GENERAL_WEBHOOK, "General Announcements"

def check_facebook_feed():
    print("Checking Facebook RSS feed for new posts...")
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        if not feed.entries:
            print("ℹ️ Feed checked: No entries found or feed is empty.")
            return

        for entry in reversed(feed.entries):
            post_id = entry.id if 'id' in entry else entry.link
            
            if post_id not in seen_posts:
                post_title = getattr(entry, 'title', '')
                post_summary = getattr(entry, 'summary', '')
                full_text = f"{post_title} {post_summary}"
                
                target_webhook, route_name = determine_webhook(full_text)
                
                if target_webhook:
                    payload = {
                        "content": f"📢 **New {route_name} Post!**\n\n{post_title}\n\n🔗 {entry.link}"
                    }
                    response = requests.post(target_webhook, json=payload)
                    if response.status_code in [200, 204]:
                        print(f"✅ Successfully routed to [{route_name}]: {post_title[:35]}...")
                        seen_posts.add(post_id)
                    else:
                        print(f"❌ Failed sending to Discord (Status {response.status_code})")
                else:
                    print(f"ℹ️ Skipping post (no matching keywords found): {post_title[:35]}...")
                    seen_posts.add(post_id)
    except Exception as e:
        print(f"⚠️ Error checking feed: {e}")

def feed_loop():
    """Background worker thread."""
    # Slight sleep on start to ensure Flask binds port first
    time.sleep(2)
    try:
        initial_feed = feedparser.parse(RSS_FEED_URL)
        for entry in initial_feed.entries:
            seen_posts.add(entry.id if 'id' in entry else entry.link)
        print(f"📦 Initialized seen posts ({len(seen_posts)} existing posts recorded).")
    except Exception as e:
        print(f"⚠️ Initial feed parse error: {e}")

    print("🚀 Bot background loop started!")
    while True:
        check_facebook_feed()
        time.sleep(CHECK_INTERVAL)

# ==========================================
# 4. FLASK SERVER SETUP
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Facebook to Discord Router Bot is running live!", 200

# Start background feed monitor
worker_thread = threading.Thread(target=feed_loop, daemon=True)
worker_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)