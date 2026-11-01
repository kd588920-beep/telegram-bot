import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_users(users):
    with open(DB_FILE, "w") as f: json.dump(users, f)
users = load_users()

# --- TUMI EKHANE PRICE CHANGE KORTE PARBE ---
UPI_ID = "koushik@upi"  # Tomar UPI ID ekhane bosao
YOUR_TELEGRAM = "@Koushik" # Tomar Telegram username

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇮🇳 India - Pay via UPI", callback_data="INDIA")],
        [InlineKeyboardButton("🇧🇩 Bangladesh - Pay via bKash / Nagad", callback_data="BANGLADESH")]
    ]
    await update.message.reply_text(
        "🌍 Select Your Country\n\nPlease select your country to continue:\n🇮🇳 India - Pay via UPI\n🇧🇩 Bangladesh - Pay via bKash / Nagad",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data
    name = query.from_user.first_name

    if data in ["INDIA", "BANGLADESH"]:
        country = data
        users[user_id] = {"country": country, "name": name, "plan": "Bronze", "balance": "₹0.00", "selected_plan": ""}
        save_users(users)

        currency_text = "Prices shown in ₹ (INR)" if country == "INDIA" else "Prices shown in ৳ (BDT)"
        pay_text = "Payments via UPI (auto-verify)" if country == "INDIA" else "Payments via bKash / Nagad"

        await query.edit_message_text(f"✅ Country set to {country} {'🇮🇳' if country=='INDIA' else '🇧🇩'}\n\n💰 {currency_text}\n💳 {pay_text}")

        # Welcome + Plan selection with BIG Reply Keyboard like Shinigami
        reply_keyboard = [
            ["Buy 1 Days", "Buy 7 Days"],
            ["Buy 30 Days", "My Balance"]
        ]
        await query.message.reply_text(
            f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n❤️‍🔥 Plan: Bronze\n💰 Balance: ₹0.00\n🌍 Country: {country}\n\n🚀 Select an option below to get started:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    name = update.effective_user.first_name
    
    if user_id not in users:
        await start(update, context)
        return

    country = users[user_id].get("country", "INDIA")

    if text.startswith("Buy"):
        # Day Select -> Game Option (Tomar cheyechile eta)
        users[user_id]["selected_plan"] = text
        save_users(users)
        
        game_keyboard = [
            ["🎮 CARROM"],
            ["🎮 Free Fire", "🎮 8 Ball Pool"],
            ["❌ Cancel"]
        ]
        await update.message.reply_text(
            f"🎁 {text} Plan Selected\n\n🎮 Select a Game:",
            reply_markup=ReplyKeyboardMarkup(game_keyboard, resize_keyboard=True)
        )

    elif "CARROM" in text:
        plan = users[user_id].get("selected_plan", "1 Days")
        await update.message.reply_text(
            f"🎮 CARROM DISC POOL\n\n📦 Plan: {plan}\n💰 Price: ₹99 for {plan}\n\n💳 UPI ID: {UPI_ID}\n\n1. UPI te payment koro\n2. Screenshot pathao {YOUR_TELEGRAM} e\n3. Auto delivery peye jabe\n\n",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I Paid", callback_data="PAID")]])
        )
    
    elif "Free Fire" in text:
        await update.message.reply_text("🔥 Free Fire - Diamond list coming soon... Contact admin")
    
    elif "8 Ball Pool" in text:
        await update.message.reply_text("🎱 8 Ball Pool - Coins list coming soon... Contact admin")

    elif "Cancel" in text:
        reply_keyboard = [
            ["Buy 1 Days", "Buy 7 Days"],
            ["Buy 30 Days", "My Balance"]
        ]
        await update.message.reply_text("Cancelled. Select again:", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)

def main():
    threading.Thread(target=run_flask).start()
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == "__main__":
    main()
