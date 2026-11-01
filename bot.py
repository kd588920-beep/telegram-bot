import json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users:
        country = users[user_id].get("country", "India")
        balance = users[user_id].get("balance", 0)
        name = update.effective_user.first_name
        await update.message.reply_text(f"👑 Welcome Back! 🌍 {country} 💰 ₹{balance}\n\n👤 Name: {name}\nPlan: 👑 ADMIN - Boss")
        return
    keyboard = [
        [InlineKeyboardButton("🇮🇳 INDIA - UPI", callback_data="country_india")],
        [InlineKeyboardButton("🇧🇩 BANGLADESH - bKash/Nagad", callback_data="country_bd")]
    ]
    await update.message.reply_text("Please select your country to continue:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    if query.data.startswith("country_"):
        country = "India" if query.data == "country_india" else "Bangladesh"
        users[user_id] = {"country": country, "balance": 0.00}
        save_users(users)
        name = query.from_user.first_name
        await query.edit_message_text(f"✅ Country set to {country}\n\n👑 Welcome to SHINIGAMI Bot!\n👤 Name: {name}\nPlan: 👑 ADMIN - Boss\n💰 Balance: ₹0.00\n🌍 Country: {country}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
