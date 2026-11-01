import os
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
TOKEN="928125293:AAH4v8xKhuZgm2x5nKo-XMPAh9m4QlUti8"
flask_app=Flask(__name__)
@flask_app.route('/')
def home(): return "Bot LIVE 24h - OK"
async def start(update, context):
 keyboard=[["1 Din Kharide"],["7 Din Kharide"],["30 Din Kharide"]]
 await update.message.reply_text("Bot Chalu!",reply_markup=ReplyKeyboardMarkup(keyboard,resize_keyboard=True))
def run_bot():
 app=Application.builder().token(TOKEN).build()
 app.add_handler(CommandHandler("start",start))
 app.run_polling(drop_pending_updates=True)
if __name__=="__main__":
 threading.Thread(target=run_bot,daemon=False).start()
 port=int(os.environ.get("PORT",10000))
 flask_app.run(host="0.0.0.0",port=port)
