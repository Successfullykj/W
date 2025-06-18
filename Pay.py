import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Config
WALLET = "47HxtCmFXxqVzQSGjQgBnDC1LRTrokf3aMFocbWQRxYzjhjxkfLGjzwE3PJhrCtdQkXPunr8cZZBAiEmY5W46V1UV8mFMZh"
BOT_TOKEN = "7971605755:AAHAh9QO9BVS9dLAWYB4ZZ1XxCGZ-15Ut2M"
CHAT_ID = "-1002712669499"

API_URL = f"https://moneroocean.stream/api/user/{WALLET}"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_confirmed = 0.0

def get_confirmed():
    try:
        r = requests.get(API_URL)
        if r.status_code == 200:
            data = r.json()
            return float(data["stats"]["xmr_confirmed"])
    except Exception as e:
        print("Error:", e)
    return None

def send_message(text):
    requests.get(f"{TG_API}/sendMessage", params={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def check_xmr_loop():
    global last_confirmed
    print("🔁 XMR confirmation monitor started...")
    while True:
        current = get_confirmed()
        if current is not None:
            if current > last_confirmed:
                diff = current - last_confirmed
                message = (
                    f"✅ *New XMR Confirmed!*\n\n"
                    f"💰 *Amount:* `{diff:.12f}` XMR\n"
                    f"📊 *Total Confirmed:* `{current:.12f}` XMR"
                )
                send_message(message)
                last_confirmed = current
            elif last_confirmed == 0.0:
                last_confirmed = current
        time.sleep(300)

def handle_command(command):
    if command == "/start":
        return "👋 Bot is running and monitoring your Monero wallet for confirmations."
    elif command == "/help":
        return (
            "🛠 *Available Commands:*\n"
            "`/start` - Start the bot\n"
            "`/balance` - Show current confirmed XMR\n"
            "`/help` - Show this help message"
        )
    elif command == "/balance":
        current = get_confirmed()
        if current is not None:
            return f"💰 *Confirmed XMR Balance:*\n`{current:.12f}` XMR"
        else:
            return "⚠️ Could not fetch balance."
    else:
        return "❓ Unknown command. Use /help"

class TelegramHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        data = json.loads(body)

        if "message" in data and "text" in data["message"]:
            text = data["message"]["text"]
            chat_id = str(data["message"]["chat"]["id"])
            if chat_id == CHAT_ID or CHAT_ID.startswith("-"):  # private or group
                response = handle_command(text.strip())
                if response:
                    requests.get(f"{TG_API}/sendMessage", params={
                        "chat_id": chat_id,
                        "text": response,
                        "parse_mode": "Markdown"
                    })

        self.send_response(200)
        self.end_headers()

def start_bot_webhook():
    server = HTTPServer(('0.0.0.0', 8000), TelegramHandler)
    print("🌐 Telegram command listener started on port 8000")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=check_xmr_loop, daemon=True).start()
    start_bot_webhook()
