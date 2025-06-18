import time
import requests
import threading

# Config
WALLET = "47HxtCmFXxqVzQSGjQgBnDC1LRTrokf3aMFocbWQRxYzjhjxkfLGjzwE3PJhrCtdQkXPunr8cZZBAiEmY5W46V1UV8mFMZh"
BOT_TOKEN = "7971605755:AAHAh9QO9BVS9dLAWYB4ZZ1XxCGZ-15Ut2M"
CHAT_ID = "-1002712669499"

API_URL = f"https://moneroocean.stream/api/user/{WALLET}"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_confirmed = 0.0
last_update_id = 0

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

def handle_command(text):
    if text == "/start":
        return "👋 Bot is running and monitoring your Monero wallet for confirmations."
    elif text == "/help":
        return (
            "🛠 *Available Commands:*\n"
            "`/start` - Start the bot\n"
            "`/balance` - Show current confirmed XMR\n"
            "`/help` - Show this help message"
        )
    elif text == "/balance":
        current = get_confirmed()
        if current is not None:
            return f"💰 *Confirmed XMR Balance:*\n`{current:.12f}` XMR"
        else:
            return "⚠️ Could not fetch balance."
    else:
        return "❓ Unknown command. Use /help"

def check_commands_loop():
    global last_update_id
    print("💬 Telegram polling started...")
    while True:
        try:
            url = f"{TG_API}/getUpdates?timeout=10&offset={last_update_id + 1}"
            r = requests.get(url)
            updates = r.json()["result"]

            for update in updates:
                last_update_id = update["update_id"]
                if "message" in update:
                    message = update["message"]
                    chat_id = str(message["chat"]["id"])
                    if chat_id != CHAT_ID:
                        continue
                    text = message.get("text", "").strip()
                    if text:
                        response = handle_command(text)
                        if response:
                            send_message(response)
        except Exception as e:
            print("Polling error:", e)

        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=check_xmr_loop, daemon=True).start()
    check_commands_loop()
