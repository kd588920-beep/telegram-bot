import os
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
QR_FILE_ID = os.getenv("QR_FILE_ID")
PLANS = {"1 Day":30, "3 Day":70, "7 Day":120, "15 Day":200, "30 Day":350}

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Koushik Gaming Bot LIVE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1 Day","3 Day"], ["7 Day","15 Day"], ["30 Day"]]
    await update.message.reply_text("🔥 Koushik Gaming India 🔥\nNiche theke plan select koro:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt not in PLANS: return
    price = PLANS[txt]
    cap = f"✅ {txt} - ₹{price}\n\n📱 UPI QR Scan koro payment er jonno\nPayment kore screenshot pathao\n\n🇮🇳 Jio Payment - PhonePe"
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=QR_FILE_ID, caption=cap)

async def run_telegram():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plan))
    print("Bot polling started...")
    await app.run_polling()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_telegram())
