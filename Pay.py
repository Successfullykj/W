import time
import requests

WALLET = "47HxtCmFXxqVzQSGjQgBnDC1LRTrokf3aMFocbWQRxYzjhjxkfLGjzwE3PJhrCtdQkXPunr8cZZBAiEmY5W46V1UV8mFMZh"
BOT_TOKEN = "7971605755:AAHAh9QO9BVS9dLAWYB4ZZ1XxCGZ-15Ut2M"
CHAT_ID = "-1002712669499"

API_URL = f"https://moneroocean.stream/api/user/{WALLET}"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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

def send_message(new_amt, total_amt):
    text = f"✅ New XMR Confirmed!\n\n💰 Amount: `{new_amt:.12f}` XMR\n📊 Total Confirmed: `{total_amt:.12f}` XMR"
    requests.get(TG_API, params={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    print("🔁 XMR confirmation bot started...")
    while True:
        current = get_confirmed()
        if current is not None:
            if current > last_confirmed:
                diff = current - last_confirmed
                send_message(diff, current)
                last_confirmed = current
            elif last_confirmed == 0.0:
                last_confirmed = current
        time.sleep(300)  # ⏱️ Check every 5 minutes
