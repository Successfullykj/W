import time import requests import threading from telegram import Update, Bot from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

Config

WALLET = "47HxtCmFXxqVzQSGjQgBnDC1LRTrokf3aMFocbWQRxYzjhjxkfLGjzwE3PJhrCtdQkXPunr8cZZBAiEmY5W46V1UV8mFMZh" BOT_TOKEN = "7971605755:AAHAh9QO9BVS9dLAWYB4ZZ1XxCGZ-15Ut2M" CHAT_ID = "-1002712669499" API_URL = f"https://moneroocean.stream/api/user/{WALLET}"

last_confirmed = 0.0

def get_confirmed(): try: r = requests.get(API_URL) if r.status_code == 200: data = r.json() return float(data["stats"]["xmr_confirmed"]) except Exception as e: print("Error:", e) return None

async def send_message(text: str, context: ContextTypes.DEFAULT_TYPE): await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("👋 Bot is running and monitoring your Monero wallet for confirmations.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "🛠 Available Commands:\n" "/start - Start the bot\n" "/balance - Show current confirmed XMR\n" "/help - Show this help message", parse_mode="Markdown" )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE): current = get_confirmed() if current is not None: await update.message.reply_text(f"💰 Confirmed XMR Balance:\n{current:.12f} XMR", parse_mode="Markdown") else: await update.message.reply_text("⚠️ Could not fetch balance.")

def check_xmr_loop(application): global last_confirmed print("🔁 XMR confirmation monitor started...") while True: current = get_confirmed() if current is not None: if current > last_confirmed: diff = current - last_confirmed message = ( f"✅ New XMR Confirmed!\n\n" f"💰 Amount: {diff:.12f} XMR\n" f"📊 Total Confirmed: {current:.12f} XMR" ) application.create_task(send_message(message, application)) last_confirmed = current elif last_confirmed == 0.0: last_confirmed = current time.sleep(300)

if name == "main": app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("balance", balance))

threading.Thread(target=check_xmr_loop, args=(app,), daemon=True).start()

print("🚀 Bot is running...")
app.run_polling()

