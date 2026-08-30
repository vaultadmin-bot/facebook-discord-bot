# ==========================================
# 4. FLASK SERVER SETUP & WEBHOOK ENDPOINT
# ==========================================
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def receive_post():
    data = request.get_json() or {}
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
            return jsonify({"status": "discord_error", "code": response.status_code}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
