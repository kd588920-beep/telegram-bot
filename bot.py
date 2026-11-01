import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7189081595
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭕ Buy 1 Days", callback_data="buy1"), InlineKeyboardButton("⭕ Buy 3 Days", callback_data="buy3")],
        [InlineKeyboardButton("⭕ Buy 7 Days", callback_data="buy7"), InlineKeyboardButton("⭕ Buy 15 Days", callback_data="buy15")],
        [InlineKeyboardButton("⭕ Buy 30 Days", callback_data="buy30"), InlineKeyboardButton("📦 Stock", callback_data="stock")],
        [InlineKeyboardButton("💸 Add Funds", callback_data="addfund"), InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("📂 Get Files", callback_data="getfiles")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    db = load_db()
    if user_id in db and "country" in db[user_id]:
        bal = db[user_id].get('balance', 0.0)
        plan = "👑 ADMIN" if user_id == str(ADMIN_ID) else db[user_id].get('plan', 'Bronze')
        country = db[user_id]['country']
        text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n🌍 Country: {country}\n\n🚀 Select an option below to get started:"
        await update.message.reply_text(text, reply_markup=main_keyboard())
    else:
        btn = [[InlineKeyboardButton("🇮🇳 INDIA - UPI", callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH - bKash/Nagad", callback_data="bd")]]
        await update.message.reply_text("Please select your country to continue:", reply_markup=InlineKeyboardMarkup(btn))

async def country_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    db = load_db()
    if user_id not in db:
        db[user_id] = {"balance": 0.0, "plan": "Bronze"}
    db[user_id]["country"] = "India" if query.data == "in" else "Bangladesh"
    save_db(db)
    await query.answer()
    name = query.from_user.first_name
    bal = db[user_id]['balance']
    plan = "👑 ADMIN" if user_id == str(ADMIN_ID) else db[user_id]['plan']
    country = db[user_id]['country']
    text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n🌍 Country: {country}\n\n🚀 Select an option below to get started:"
    await query.edit_message_text(text, reply_markup=main_keyboard())

async def buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    db = load_db()
    bal = db.get(user_id, {}).get('balance', 0.0)
    await query.answer()
    if query.data == "stock":
        await query.message.reply_text("📦 Stock: 125 Accounts Available ✅")
    elif query.data == "balance":
        await query.message.reply_text(f"💰 Tomar Balance: ₹{bal:.2f}\n\nAdd Funds korte niche button chapo.", reply_markup=main_keyboard())
    elif query.data == "addfund":
        await query.message.reply_text("💸 Add Funds:\n\n🇮🇳 UPI ID: tomar_upi@okaxis\n🇧🇩 bKash: 01XXXXXXXXX\n\nPay kore screenshot dao admin ke: @YourAdminUsername")
    elif query.data == "getfiles":
        await query.message.reply_text("📂 Get Files: Age kono plan keno!")
    elif "buy" in query.data:
       
