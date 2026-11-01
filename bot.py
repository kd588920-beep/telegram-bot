import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"
UPI_ID = "Jio Payments - 2754"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_users(u):
    with open(DB_FILE, "w") as f: json.dump(u, f)

users = load_users()
PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹200","30 Days":"₹500"}

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🎮 Carrom Pool", callback_data="game_Carrom Pool")],
        [InlineKeyboardButton("🎮 8 Ball Pool", callback_data="game_8 Ball Pool")],
    ]
    await update.message.reply_text("Game Select Koro:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("game_"):
        game_name = data.split("_",1)[1]
        keyboard = [
            [InlineKeyboardButton(f"{k} - {v}", callback_data=f"plan_{game_name}_{k}_{v}") for k,v in list(PRICES.items())[:2]],
            [InlineKeyboardButton(f"{k} - {v}", callback_data=f"plan_{game_name}_{k}_{v}") for k,v in list(PRICES.items())[2:]]
        ]
        await query.edit_message_text(f"{game_name} er jonno Plan Select Koro:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("plan_"):
        _, game_name, plan, price = data.split("_",3)
        caption = (
            f"🎮 {game_name}\n"
            f"📦 Plan: {plan}\n"
            f"💰 Price: {price}\n\n"
            f"💳 UPI ID: {UPI_ID}\n\n"
            f"📲 QR scan kore payment koro"
        )
        await query.message.reply_photo(photo=open("qr.jpg", "rb"), caption=caption)

def main():
    threading.Thread(target=run_flask).start()
    app_builder = Application.builder().token(BOT_TOKEN).build()
    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CallbackQueryHandler(button_handler))
    app_builder.run_polling()

if __name__ == "__main__":
    main()
