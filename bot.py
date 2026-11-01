import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot Live Hai! /start kaam kar raha hai")

async def run_bot_async():
    token = os.environ.get("BOT_TOKEN")
    print(f"Token found: {bool(token)}")
    if not token:
        print("ERROR: BOT_TOKEN not found!")
        return
    bot_app = Application.builder().token(token).build()
    bot_app.add_handler(CommandHandler("start", start))
    print("Bot Started Polling...")
    await bot_app.run_polling()

def run_bot():
    asyncio.run(run_bot_async())

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)
