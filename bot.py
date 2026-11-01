import os, threading
from flask import Flask
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
TOKEN="928125293:AAH4v8xKhuZgm2x5nKo-XMPAh9m4QlUti8"
app=Flask(__name__)
def home(): return "Bot LIVE"
app.add_url_rule('/', 'home', home)
KEYBOARD=ReplyKeyboardMarkup([["1 Day","3 Day"],["7 Day","15 Day"],["30 Day"]], resize_keyboard=True)
async def start(update, context):
 await update.message.reply_text("Select plan:", reply_markup=KEYBOARD)
async def buy(update, context):
 t=update.message.text
 if "1 Day" in t:
  await update.message.reply_text("1 Day - 30 Taka")
 elif "3 Day" in t:
  await update.message.reply_text("3 Day - 70 Taka")
 elif "7 Day" in t:
  await update.message.reply_text("7 Day - 120 Taka")
 elif "15 Day" in t:
  await update.message.reply_text("15 Day - 200 Taka")
 elif "30 Day" in t:
  await update.message.reply_text("30 Day - 350 Taka")
def run_flask():
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
def run_bot():
 a=Application.builder().token(TOKEN).build()
 a.add_handler(CommandHandler("start", start))
 a.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buy))
 a.run_polling()
if __name__=="__main__":
 threading.Thread(target=run_flask, daemon=True).start()
 run_bot()
