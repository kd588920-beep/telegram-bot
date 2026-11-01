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

# Niche Menu Design (SHINIGAMI Style)
def get_main_menu():
    keyboard = [
        [KeyboardButton("🎯 Buy 1 Days"), KeyboardButton("🎯 Buy 3 Days")],
        [KeyboardButton("🎯 Buy 7 Days"), KeyboardButton("🎯 Buy 15 Days")],
        [KeyboardButton("🎯 Buy 30 Days"), KeyboardButton("📦 Stock")],
        [KeyboardButton("➕ Add Funds"), KeyboardButton("💰 Balance")],
        [KeyboardButton("📁 Get Files")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹200","15 Days":"₹350","30 Days":"₹500"}

async def start(update, context):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👑 Welcome to SHINIGAMI Bot!\n\n"
        f"👤 Name: {user_name}\n"
        f"🏅 Plan: Bronze\n"
        f"💰 Balance: ₹0.00\n"
        f"🇮🇳 Country: India\n\n"
        f"🚀 Select an option below to get started:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())

async def handle_message(update, context):
    text = update.message.text
    
    if "Buy" in text:
        # Jemon Buy 1 Days click korle
        for plan in PRICES:
            if plan in text:
                price = PRICES[plan]
                caption = f"🎁 {plan} Plan Selected\n💰 Price: {price}\n\n💳 UPI ID: {UPI_ID}\n\n📲 QR scan kore pay koro"
                try:
                    await update.message.reply_photo(photo=open("qr.jpg", "rb"), caption=caption)
                except:
                    await update.message.reply_text(caption)
                return
    
    if "Stock" in text:
        await update.message.reply_text("📦 Stock: All Plans Available ✅")
    elif "Add Funds" in text:
        await update.message.reply_text(f"➕ Add Funds\n\n💳 UPI ID: {UPI_ID}\n\nQR scan kore payment koro", reply_markup=get_main_menu())
    elif "Balance" in text:
        await update.message.reply_text(f"💰 Your Balance: ₹0.00", reply_markup=get_main_menu())
    elif "Get Files" in text:
        await update.message.reply_text("📁 Files - Contact Admin for files", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Niche Menu theke select koro 👇", reply_markup=get_main_menu())

def main():
    threading.Thread(target=run_flask).start()
    app_builder = Application.builder().token(BOT_TOKEN).build()
    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_builder.run_polling()

if __name__ == "__main__":
    main()
