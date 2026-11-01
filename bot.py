import os
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
UPI_ID = "Jio Payments - 2754"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹200","15 Days":"₹350","30 Days":"₹500"}

def get_main_menu():
    keyboard = [
        [KeyboardButton("🎯 Buy 1 Days"), KeyboardButton("🎯 Buy 3 Days")],
        [KeyboardButton("🎯 Buy 7 Days"), KeyboardButton("🎯 Buy 15 Days")],
        [KeyboardButton("🎯 Buy 30 Days"), KeyboardButton("📦 Stock")],
        [KeyboardButton("➕ Add Funds"), KeyboardButton("💰 Balance")],
        [KeyboardButton("📁 Get Files")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_game_menu():
    keyboard = [
        [KeyboardButton("🃏 CARROM")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update, context):
    context.user_data.clear()
    name = update.effective_user.first_name
    text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: Bronze\n💰 Balance: ₹0.00\n🇮🇳 Country: India\n\n🚀 Select an option below to get started:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

async def handle_message(update, context):
    msg = update.message.text
    if "Buy" in msg and "Days" in msg:
        for plan in PRICES:
            if plan in msg:
                context.user_data['plan'] = plan
                context.user_data['price'] = PRICES[plan]
                await update.message.reply_text(f"🎁 {plan} Plan Selected")
                await update.message.reply_text("🎮 Select a Game:", reply_markup=get_game_menu())
                return
    if "CARROM" in msg.upper():
        plan = context.user_data.get('plan','1 Days')
        price = context.user_data.get('price','₹70')
        caption = f"🎁 {plan} Plan - CARROM\n💰 Price: {price}\n💳 UPI: {UPI_ID}\n\n📲 QR scan kore pay koro"
        try:
            await update.message.reply_photo(photo=open("qr.jpg","rb"), caption=caption, reply_markup=get_main_menu())
        except:
            await update.message.reply_text(caption, reply_markup=get_main_menu())
        return
    if "Cancel" in msg:
        await update.message.reply_text("❌ Cancelled", reply_markup=get_main_menu())
        await start(update, context)

def main():
    threading.Thread(target=run_flask).start()
    app_b = Application.builder().token(BOT_TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_b.run_polling()

if __name__ == "__main__":
    main()
