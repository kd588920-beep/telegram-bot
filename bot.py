import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

web = Flask(__name__)

@web.route('/')
def home():
    return "Bot Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot Live! Bolo ki help lagbe?\n\n1 Day = Rs 30\n3 Day = Rs 70")

def run_bot():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        return
    bot_app = ApplicationBuilder().token(token).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)
