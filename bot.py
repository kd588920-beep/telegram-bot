import json, os, asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Live!"
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}
def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)
users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🇮🇳 INDIA", callback_data="INDIA")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select your country:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    country = query.data
    users[user_id] = {"country": country}
    save_users(users)
    await query.edit_message_text(f"You selected {country}")

async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)

def main():
    threading.Thread(target=run_flask).start()
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == "__main__":
    main()
