import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

PLANS = {
    "1 Day": 30,
    "3 Day": 70,
    "7 Day": 150,
    "15 Day": 280,
    "30 Day": 500
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1 Day", "3 Day"], ["7 Day", "15 Day"], ["30 Day"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🔥 Koushik Gaming India 🔥\nNiche se plan select karo:",
        reply_markup=reply_markup
    )

async def handle_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in PLANS:
        price = PLANS[text]
        qr_path = "qr.jpg"
        if os.path.exists(qr_path):
            await update.message.reply_photo(
                photo=open(qr_path, 'rb'),
                caption=f"✅ {text} - ₹{price}\n\n📱 UPI QR Scan karo payment ke liye\nPayment karke screenshot bhejo"
            )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plan))
    app.run_polling()

if __name__ == "__main__":
    main()
