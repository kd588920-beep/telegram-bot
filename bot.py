import os
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("9281252293:AAHAv8xkHuZqm2w5nk0-XWPaR9n4QlLutI8")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot LIVE 24h - OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1 Din Kharide"], ["7 Din Kharide"], ["30 Din Kharide"]]
    await update.message.reply_text("Stock - 1 Din:0  7 Din:0  30 Din:0\nHlw Main hu Bot!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
