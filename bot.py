import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7189081595
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 SHOP", callback_data="shop"), InlineKeyboardButton("💰 Add Funds", callback_data="addfund")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile"), InlineKeyboardButton("📞 Support", callback_data="support")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    db = load_db()
    # Jodi user age country select kore thake - direct welcome
    if user_id in db and "country" in db[user_id]:
        bal = db[user_id].get('balance', 0.0)
        if user_id == str(ADMIN_ID):
            plan = "👑 ADMIN - Boss"
        else:
            plan = db[user_id].get('plan', 'Free User')
        country = db[user_id]['country']
        text = f"👑 Welcome Back to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n🌍 Country: {country}\n\n🚀 Select an option below:"
        await update.message.reply_text(text, reply_markup=main_keyboard())
    else:
        # Prothom bar
        btn = [[InlineKeyboardButton("🇮🇳 INDIA - UPI", callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH - bKash/Nagad", callback_data="bd")]]
        await update.message.reply_text("Please select your country to continue:", reply_markup=InlineKeyboardMarkup(btn))

async def country_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    db = load_db()
    if user_id not in db:
        db[user_id] = {"balance": 0.0, "plan": "Free User"}
    db[user_id]["country"] = "India" if query.data == "in" else "Bangladesh"
    save_db(db)
    await query.answer()
    name = query.from_user.first_name
    bal = db[user_id]['balance']
    plan = "👑 ADMIN - Boss" if user_id == str(ADMIN_ID) else db[user_id]['plan']
    country = db[user_id]['country']
    text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n🌍 Country: {country}\n\n🚀 Select an option below to get started:"
    await query.edit_message_text(text, reply_markup=main_keyboard())

async def makevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: 
        await update.message.reply_text("Use: /makevip USER_ID")
        return
    uid = context.args[0]
    db = load_db()
    if uid in db:
        db[uid]['plan'] = "Vip 🔥 VIP/Reseller"
        save_db(db)
        await update.message.reply_text(f"✅ {uid} ke VIP banano holo!")
    else:
        await update.message.reply_text("User not found! User ke ekbar /start korte bolo.")

async def removevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    uid = context.args[0]
    db = load_db()
    if uid in db:
        db[uid]['plan'] = "Free User"
        save_db(db)
        await update.message.reply_text(f"✅ {uid} ke Free kora holo!")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Tomar ID: {update.effective_user.id}")

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("makevip", makevip))
    app.add_handler(CommandHandler("removevip", removevip))
    app.add_handler(CallbackQueryHandler(country_select, pattern="^(in|bd)$"))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
