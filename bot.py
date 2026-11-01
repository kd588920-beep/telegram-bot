import os, threading
from flask import Flask
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = "9281252293:AAH60fX8YBldlAUzJREOlVGPYVX9kfD-9sQ"
QR_FILE = "qr.jpg" # GitHub e upload kora QR

app = Flask(__name__)
@app.route('/')
def home():
    return "Koushik Gaming Bot LIVE - India"

KEYBOARD = ReplyKeyboardMarkup(
    [["1 Day", "3 Day"], ["7 Day", "15 Day"], ["30 Day"]],
    resize_keyboard=True
)

PRICES = {
    "1 Day": "₹30",
    "3 Day": "₹70",
    "7 Day": "₹120",
    "15 Day": "₹200",
    "30 Day": "₹350"
}

async def start(update, context):
    await update.message.reply_text(
        "🔥 Koushik Gaming India 🔥\nNiche theke plan select koro:",
        reply_markup=KEYBOARD
    )

async def buy(update, context):
    text = update.message.text
    for plan in PRICES:
        if plan in text:
            price = PRICES[plan]
            caption = f"✅ {plan} - {price}\n\n📱 UPI QR Scan koro payment er jonno\nPayment kore screenshot pathao @YourUsername\n\n🇮🇳 Jio Payment - PhonePe"
            try:
                with open(QR_FILE, 'rb') as qr:
                    await update.message.reply_photo(photo=qr, caption=caption)
            except:
                await update.message.reply_text(caption + "\n\n(QR upload koro GitHub e qr.jpg naam e)")
            break

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def run_bot():
    a = Application.builder().token(TOKEN).build()
    a.add_handler(CommandHandler("start", start))
    a.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buy))
    a.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
