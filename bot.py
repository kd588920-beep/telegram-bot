import os, threading, asyncio
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def country_keyboard():
    return ReplyKeyboardMarkup([["🇮🇳 INDIA"], ["🇧🇩 BANGLADESH"]], resize_keyboard=True)

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["🔥 Buy 1 Days", "🔥 Buy 3 Days"],
        ["🔥 Buy 7 Days", "🔥 Buy 15 Days"],
        ["🔥 Buy 30 Days", "📦 Stock"],
        ["💳 Add Funds", "💰 Balance"],
        ["📁 Get Files"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌍 Select Your Country\n\nPlease select your country to continue:\n\n🇮🇳 India - Pay via UPI\n🇧🇩 Bangladesh - Pay via bKash / Nagad"
    await update.message.reply_text(text, reply_markup=country_keyboard())

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    name = update.effective_user.first_name
    
    # Country Select
    if "INDIA" in msg.upper():
        context.user_data['country'] = "India"
        welcome = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n👑 Plan: Vip 👑 VIP/Reseller\n💰 Balance: ₹0.00\n🇮🇳 Country: India\n\n💎 CARROM\n🏅 Your Medal: Bronze 🥉\n\n📋 Price List\n• 1 Days - ₹60\n• 3 Days - ₹140\n• 7 Days - ₹220\n• 15 Days - ₹350\n• 30 Days - ₹550\n\n🚀 Select an option below to get started:"
        await update.message.reply_text(welcome, reply_markup=main_keyboard())
        return
        
    if "BANGLADESH" in msg.upper():
        context.user_data['country'] = "Bangladesh"
        welcome = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n👑 Plan: Vip 👑 VIP/Reseller\n💰 Balance: ৳0.00\n🇧🇩 Country: Bangladesh\n\n💎 CARROM\n🏅 Your Medal: Bronze 🥉\n\n📋 Price List\n• 1 Days - 120৳\n• 3 Days - 280৳\n• 7 Days - 450৳\n• 15 Days - 700৳\n• 30 Days - 1100৳\n\n🚀 Select an option below to get started:"
        await update.message.reply_text(welcome, reply_markup=main_keyboard())
        return

    # Other buttons
    if "Buy" in msg:
        await update.message.reply_text(f"✅ {msg} selected!\nAdmin: @Koushikgaming09", reply_markup=main_keyboard())
    elif "Stock" in msg:
        await update.message.reply_text("📦 Current Stock:\n✅ 1 Days: 5 keys\n✅ 3 Days: 3 keys\n✅ 7 Days: 3 keys\n✅ 15 Days: 1 keys\n✅ 30 Days: 2 keys", reply_markup=main_keyboard())
    elif "Balance" in msg:
        await update.message.reply_text(f"👤 Name: {name}\n💰 Balance: ₹0.00", reply_markup=main_keyboard())
    else:
        await update.message.reply_text("Niche theke select koro 👇", reply_markup=main_keyboard())

def run_bot():
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None, close_loop=False)

web = Flask(__name__)
@web.route('/')
def home(): return "Bot is Live!"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
