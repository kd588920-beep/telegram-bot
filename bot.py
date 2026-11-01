import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
QR_FILE_ID = os.getenv("QR_FILE_ID")

PLANS = {"1 Day": 30, "3 Day": 70, "7 Day": 120, "15 Day": 200, "30 Day": 350}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1 Day", "3 Day"], ["7 Day", "15 Day"], ["30 Day"]]
    await update.message.reply_text("🔥 Koushik Gaming - Plan Select Karo:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in PLANS:
        return
    price = PLANS[text]
    caption = f"✅ {text} - ₹{price}\n\n📱 UPI QR Scan karo payment ke liye\nPayment karke screenshot bhejo\n\n🇮🇳 Jio Payment - PhonePe"
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=QR_FILE_ID, caption=caption)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plan))
    app.run_polling()

if __name__ == "__main__":
    main()
