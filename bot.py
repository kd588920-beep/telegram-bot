import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
UPI_ID = "Jio Payments - 2754"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹200","30 Days":"₹500"}

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🎮 Carrom Pool", callback_data="game_Carrom Pool")],
        [InlineKeyboardButton("🎮 8 Ball Pool", callback_data="game_8 Ball Pool")]
    ]
    await update.message.reply_text("🎮 Select a Game:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("game_"):
        game = data.split("game_",1)[1]
        keyboard = [
            [InlineKeyboardButton(f"1 Days - ₹70", callback_data=f"buy_{game}_1 Days_₹70"),
             InlineKeyboardButton(f"3 Days - ₹140", callback_data=f"buy_{game}_3 Days_₹140")],
            [InlineKeyboardButton(f"7 Days - ₹200", callback_data=f"buy_{game}_7 Days_₹200"),
             InlineKeyboardButton(f"30 Days - ₹500", callback_data=f"buy_{game}_30 Days_₹500")]
        ]
        await query.edit_message_text(f"✅ {game} Selected\n\n📦 {game} er jonno Plan Select Koro:", reply_markup=InlineKeyboardMarkup(keyboard))

    if data.startswith("buy_"):
        _, game, plan, price = data.split("_",3)
        text = f"🎁 {plan} Plan - {game}\n💰 Price: {price}\n\n💳 UPI ID: {UPI_ID}\n\n📲 QR scan kore pay koro\n\nPay korar por screenshot pathao"
        await query.message.reply_photo(photo=open("qr.jpg","rb"), caption=text)

def main():
    threading.Thread(target=run_flask).start()
    app_builder = Application.builder().token(BOT_TOKEN).build()
    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CallbackQueryHandler(button_handler))
    app_builder.run_polling()

if __name__ == "__main__":
    main()
