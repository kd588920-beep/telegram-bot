import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595
DB_FILE = "users.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["🔥 Buy 1 Days", "🔥 Buy 3 Days"],
        ["🔥 Buy 7 Days", "🔥 Buy 15 Days"],
        ["🔥 Buy 30 Days", "📦 Stock"],
        ["➕ Add Funds", "💰 Balance"],
        ["📁 Get Files"]
    ], resize_keyboard=True)

async def makevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Tumi admin na!")
        return
    if not context.args:
        await update.message.reply_text("Use: /makevip USER_ID")
        return
    uid = context.args[0]
    db = load_db()
    if uid not in db: db[uid] = {"balance":0, "plan":"Free User", "country":"India"}
    db[uid]["plan"] = "Vip 🔥 VIP/Reseller"
    save_db(db)
    await update.message.reply_text(f"✅ {uid} ke VIP banano holo!")

async def removevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    uid = context.args[0]
    db = load_db()
    if uid in db:
        db[uid]["plan"] = "Free User"
        save_db(db)
        await update.message.reply_text(f"✅ {uid} er VIP tule neoa holo!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("🇮🇳 INDIA - UPI", callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH - bKash/Nagad", callback_data="bd")]]
    await update.message.reply_text("Please select your country to continue:", reply_markup=InlineKeyboardMarkup(btn))

async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    name = q.from_user.first_name
    db = load_db()
    if user_id not in db:
        db[user_id] = {"balance": 0.0, "plan": "Free User", "country": "India"}
    if q.data == "in": db[user_id]["country"] = "India"
    else: db[user_id]["country"] = "Bangladesh"
    save_db(db)
    bal = db[user_id]['balance']
    plan = db[user_id]['plan']
    country = db[user_id]['country']
    text = f"✅ Country set to {country} {'🇮🇳' if country=='India' else '🇧🇩'}\n\n💰 Prices shown in {'₹ (INR)' if country=='India' else '৳ (BDT)'}\n💳 Payments via {'UPI (auto-verify)' if country=='India' else 'bKash / Nagad'}\n\n👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n🌍 Country: {country}\n\n🚀 Select an option below to get started:"
    await q.message.reply_text(text, reply_markup=main_keyboard())

def run_bot():
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("makevip", makevip))
    app.add_handler(CommandHandler("removevip", removevip))
    app.add_handler(CallbackQueryHandler(country_handler))
    app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None, close_loop=False)

web = Flask(__name__)
@web.route('/')
def home(): return "Bot Live - Admin 7189081595"
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
