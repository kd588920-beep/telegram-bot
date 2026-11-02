import os, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7260634404
PRICE = {"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}

stock = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): 
    return "☠️ SHINIGAMI Bot Running!"

def main_kb():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("💳 Buy 1 Days","💳 Buy 3 Days")
    m.add("💳 Buy 7 Days","💳 Buy 15 Days")
    m.add("💳 Buy 30 Days","📦 Stock")
    m.add("💰 Balance","➕ Add Funds")
    m.add("📁 Get Files")
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    if uid not in user_balance:
        user_balance[uid] = 0
    text = (
        "☠️ **SHINIGAMI - DEATH NOTE STORE** ☠️\n\n"
        "👁️ _I am watching you..._\n\n"
        "💀 **PLANS:**\n"
        f"1 Day - ₹{PRICE['1D']}\n"
        f"3 Days - ₹{PRICE['3D']}\n"
        f"7 Days - ₹{PRICE['7D']}\n"
        f"15 Days - ₹{PRICE['15D']}\n"
        f"30 Days - ₹{PRICE['30D']}\n\n"
        f"💰 Your Balance: ₹{user_balance[uid]}\n"
        f"🆔 Your ID: `{uid}`\n\n"
        "Choose your fate 👇"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and "Buy" in m.text)
def buy(msg):
    uid = msg.from_user.id
    mapping = {"Buy 1 Days":"1D","Buy 3 Days":"3D","Buy 7 Days":"7D","Buy 15 Days":"15D","Buy 30 Days":"30D"}
    plan = None
