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
 if "1 Day" in t: await update.message.reply_text("1 Day - 30 Taka")
 elif "3 Day" in t
