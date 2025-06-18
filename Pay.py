import time
import requests
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Config
WALLET = "47HxtCmFXxqVzQSGjQgBnDC1LRTrokf3aMFocbWQRxYzjhjxkfLGjzwE3PJhrCtdQkXPunr8cZZBAiEmY5W46V1UV8mFMZh"
BOT_TOKEN = "8067230426:AAGmGeSe7P7hlnvoCPsw7mDpm1qbtnhASq0"
CHAT_ID = -1002712669499  # use int for group

API_URL = f"https://moneroocean.stream/api/user/{WALLET}"
last_confirmed = 0.0

def get_confirmed():
    try:
        r = requests.get(API_URL)
        if r.status_code == 200:
            data = r.json()
            return float(data["stats"]["xmr_confirmed"])
    except Exception as e:
        print("Error fetching balance:", e)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Bot is running and monitoring your Monero wallet for confirmations.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛠 *Available Commands:*\n"
        "`/start` - Start the bot\n"
        "`/balance` - Show current confirmed XMR\n"
        "`/help` - Show this help message"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="Markdown")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = get_confirmed()
    if current is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"💰 *Confirmed XMR Balance:*\n`{current:.12f}` XMR", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Could not fetch balance.")

def monitor_confirmed(app):
    global last_confirmed
    while True:
        current = get_confirmed()
        if current is not None:
            if current > last_confirmed:
                diff = current - last_confirmed
                msg = (
                    f"✅ *New XMR Confirmed!*\n\n"
                    f"💰 *Amount:* `{diff:.12f}` XMR\n"
                    f"📊 *Total Confirmed:* `{current:.12f}` XMR"
                )
                app.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
                last_confirmed = current
            elif last_confirmed == 0.0:
                last_confirmed = current
        time.sleep(300)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))

    threading.Thread(target=monitor_confirmed, args=(app,), daemon=True).start()
    print("✅ Bot started and monitoring...")
    app.run_polling()
