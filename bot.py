import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot Live! Bolo ki help lagbe?")

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Tumi bolle: {update.message.text}")

def run_bot():
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)
