import os, threading
from flask import Flask
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = "9281252293:AAH60fX8YBldlAUzJREOlVGPYVX9kfD-9sQ"

app = Flask(__name__)
@app.route('/')
def home():
    return "Koushik Gaming Bot LIVE"

# 5 ta button permanent thakbe
KEYBOARD = ReplyKeyboardMarkup(
    [["1 Day", "3 Day"], ["7 Day", "15 Day"], ["30 Day"]],
    resize_keyboard=True
)

async def start(update, context):
    await update.message.reply_text(
        "🔥 Koushik Gaming 🔥\nSelect plan niche theke:",
        reply_markup=KEYBOARD
    )

async def buy(update, context):
    text = update.message.text
    if "1 Day" in text:
        await update.message.reply_text("✅ 1 Day - 30 Taka\nBkash/Nagad: 01XXXXXXXXX")
    elif "3 Day" in text:
        await update.message.reply_text("✅ 3 Day - 70 Taka\nBkash/Nagad: 01XXXXXXXXX")
    elif "7 Day" in text:
        await update.message.reply_text("✅ 7 Day - 120 Taka\nBkash/Nagad: 01XXXXXXXXX")
    elif "15 Day" in text:
        await update.message.reply_text("✅ 15 Day - 200 Taka\nBkash/Nagad: 01XXXXXXXXX")
    elif "30 Day" in text:
        await update.message.reply_text("✅ 30 Day - 350 Taka\nBkash/Nagad: 01XXXXXXXXX")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def run_bot():
    a = Application.builder().token(TOKEN).build()
    a.add_handler(CommandHandler("start", start))
    a.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buy))
    a.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
