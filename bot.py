import os
import threading
import asyncio
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Keyboard
def get_keyboard():
    keyboard = [["1 Day", "3 Day"], ["7 Day", "15 Day"], ["30 Day"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is LIVE!\n\nKoushik Gaming Bot e swagoto!\n\nNiche theke Day select koro 👇",
        reply_markup=get_keyboard()
    )

async def handle_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if day in ["1 Day", "3 Day", "7 Day", "15 Day", "30 Day"]:
        await update.message.reply_text(
            f"✅ Tumi select korecho: {day} \n\n💰 Price er jonno admin er sathe contact koro!",
            reply_markup=get_keyboard()
        )
    else:
        await update.message.reply_text("Niche theke Day select koro 👇", reply_markup=get_keyboard())

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_day))
    print("Bot Started Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None, close_loop=False)

web = Flask(__name__)
@web.route('/')
def home():
    return "Bot is Live!"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)
