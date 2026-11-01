import os
import threading
from flask import Flask
from telegram import , ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN="928125293:AAH4v8xKhuZgm2x5nKo-XMPAh9m4QlUti8"
flask_app=Flask(__name__)
@flask_app.route('/')
def home(): return "Bot LIVE - OK"

async def start(update, context):
 keyboard=[["1 Din Kharide"],["7 Din Kharide"],["30 Din Kharide"]]
 await update.message.reply_text("Stock - 1 Din:0 7 Din:0 30 Din:0\nHlw Main hu Bot, Main chalu hu!",reply_markup=ReplyKeyboardMarkup(keyboard,resize_keyboard=True))

async def buy(update, context):
 await update.message.reply_text(f"Tumi {update.message.text} select korecho. Payment system chalu hobe.")

def run_flask():
 port=int(os.environ.get("PORT",10000))
 flask_app.run(host="0.0.0.0",port=port)

def run_bot():
 app=Application.builder().token(TOKEN).build()
 app.add_handler(CommandHandler("start",start))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buy))
 app.run_polling(drop_pending_updates=True)

if __name__=="__main__":
 threading.Thread(target=run_flask,daemon=True).start()
 run_bot()

