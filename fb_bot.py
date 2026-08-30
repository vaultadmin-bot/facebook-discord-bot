import os
import requests
from flask import Flask, request, jsonify

# ==========================================
# 1. YOUR FEED & WEBHOOK CONFIGURATION
# ==========================================

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
            "magic", "mtg", "#mtg", "commander", "edh", "prerelease", "draft", 
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

seen_posts = set()

# ==========================================
# 3. ROUTING LOGIC
# ==========================================

def determine_webhook(content):
    content_lower = (content or "").lower()
    for route in ROUTES:
        for keyword in route["keywords"]:
            if keyword in content_lower:
                return route["webhook"], route["name"]
    return GENERAL_WEBHOOK, "General Announcements"

# ==========================================
# 4. FLASK SERVER & WEBHOOK RECEIVER
# ==========================================

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def receive_post():
    data = request.get_json(silent=True) or {}
    post_id = data.get('id')
    post_text = data.get('message', '')
    post_link = data.get('link', '')

    if not post_id or post_id in seen_posts:
        return jsonify({"status": "ignored", "reason": "already seen or empty"}), 200

    target_webhook, route_name = determine_webhook(post_text)

    payload = {
        "content": f"📢 **New {route_name} Post!**\n\n{post_text}\n\n🔗 {post_link}"
    }
    
    try:
        response = requests.post(target_webhook, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            seen_posts.add(post_id)
            print(f"✅ Routed Make post to [{route_name}]", flush=True)
            return jsonify({"status": "success"}), 200
        else:
            print(f"❌ Discord returned status {response.status_code}", flush=True)
            return jsonify({"status": "discord_error", "code": response.status_code}), 500
    except Exception as e:
        print(f"⚠️ Error posting to Discord: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
