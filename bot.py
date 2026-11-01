import os, threading
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters
TOKEN="928125293:AAH4v8xKhuZgm2x5nKo-XMPAh9m4QlUti8"
app=Flask(__name__)
@ app.route('/')
def home():
 return "Bot LIVE"
async def start(update, context):
 await update.message.reply_text("Bot Chalu! 24h LIVE")
async def buy(update, context):
 await update.message.reply_text(f"Buy: {update.message.text}")
def run_flask():
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
def run_bot():
 a=Application.builder().token(TOKEN).build()
 a.add_handler(CommandHandler("start", start))
 a.add_handler(MessageHandler(filters.TEXT, buy))
 a.run_polling()
if __name__=="__main__":
 threading.Thread(target=run_flask, daemon=True).start()
 run_bot()
 
