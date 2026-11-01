import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"
UPI_ID = "koushik@upi"  # <-- Ekhane tomar UPI ID bosao
YOUR_TELEGRAM = "@Koushik" 

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

# --- TOMAR FINAL PRICE ---
PRICES = {
    "1 Days": "₹70",
    "3 Days": "₹140",
    "7 Days": "₹190",
    "15 Days": "₹350",
    "30 Days": "₹570"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇮🇳 India - Pay via UPI", callback_data="INDIA")],
        [InlineKeyboardButton("🇧🇩 Bangladesh - bKash", callback_data="BANGLADESH")]
    ]
    await update.message.reply_text("🌍 Select Your Country", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data
    name = query.from_user.first_name
    if data in ["INDIA", "BANGLADESH"]:
        users[user_id] = {"country": data, "name": name, "selected_plan": ""}
        save_users(users)
        await query.edit_message_text(f"✅ Country set to {data} {'🇮🇳' if data=='INDIA' else '🇧🇩'}\n💰 Prices in ₹\n💳 Payments via UPI")
        reply_keyboard = [
            ["Buy 1 Days - ₹70", "Buy 3 Days - ₹140"],
            ["Buy 7 Days - ₹190", "Buy 15 Days - ₹350"],
            ["Buy 30 Days - ₹570", "My Balance"]
        ]
        await query.message.reply_text(
            f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n❤️‍🔥 Plan: Bronze\n💰 Balance: ₹0.00\n🌍 Country: {data}\n\n🚀 Select an option below:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    if user_id not in users:
        await start(update, context); return
    
    if "Buy" in text:
        # Extract plan like "1 Days" from "Buy 1 Days - ₹70"
        plan = text.split(" - ")[0].replace("Buy ", "")
        users[user_id]["selected_plan"] = plan
        save_users(users)
        game_keyboard = [["🎮 CARROM"], ["❌ Cancel"]]
        await update.message.reply_text(f"🎁 {plan} Plan Selected\nPrice: {PRICES.get(plan)}\n\n🎮 Select a Game:", reply_markup=ReplyKeyboardMarkup(game_keyboard, resize_keyboard=True))
    
    elif "CARROM" in text:
        plan = users[user_id].get("selected_plan", "1 Days")
        price = PRICES.get(plan, "₹70")
        caption = f"🎮 CARROM DISC POOL\n\n📦 Plan: {plan}\n💰 Price: {price}\n\n💳 UPI ID: {UPI_ID}\n\n👉 {price} Pay Now\n1. QR scan koro\n2. Screenshot {YOUR_TELEGRAM} e pathao\n3. Instant delivery!"
        try:
            with open("qr.jpg", "rb") as qr_file:
                await update.message.reply_photo(photo=qr_file, caption=caption)
        except:
            await update.message.reply_text(caption)
    
    elif "Cancel" in text:
        reply_keyboard = [["Buy 1 Days - ₹70", "Buy 3 Days - ₹140"], ["Buy 7 Days - ₹190", "Buy 15 Days - ₹350"], ["Buy 30 Days - ₹570"]]
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
