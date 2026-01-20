from flask import Flask, request, jsonify
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_SECRET = os.environ.get("BOT_SECRET")

app = Flask(__name__)

def api_url(method, params=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return url

def send_message(chat_id, reply_id, text):
    import requests
    requests.get(api_url("sendMessage", {
        "chat_id": chat_id,
        "reply_to_message_id": reply_id,
        "text": text
    }))

@app.route("/endpoint", methods=["POST"])
def webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != BOT_SECRET:
        return "Unauthorized", 403

    update = request.json

    if "message" not in update:
        return "OK"

    message = update["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    if "text" in message and message["text"].startswith("/start "):
        file_hash = message["text"].split("/start ")[1]

        origin = request.url_root.rstrip("/")
        final_link = f"{origin}/?file={file_hash}"
        final_stre = f"{origin}/?file={file_hash}&mode=inline"

        send_message(
            chat_id,
            message_id,
            f"⬇ Download:\n{final_link}\n\n▶ Stream:\n{final_stre}"
        )

    return "OK"

@app.route("/", methods=["GET"])
def download():
    file = request.args.get("file")
    mode = request.args.get("mode", "attachment")

    if not file:
        return jsonify({"ok": False, "error": "missing file"}), 404

    # Simple version: just show a message
    return jsonify({
        "ok": True,
        "message": "Streaming is handled by your Worker / CDN logic",
        "file": file,
        "mode": mode
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
