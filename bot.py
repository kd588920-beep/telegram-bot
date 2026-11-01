import os, random, string
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

# Tomar final price
PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹190","15 Days":"₹350","30 Days":"₹570"}
VIP_PRICES = {"1 Days":40,"3 Days":100,"7 Days":150,"15 Days":300,"30 Days":500}

# Demo Stock - tumi pore change korte parbe
STOCK = {"CARROM": 5}
USERS = {} # balance store

def gen_key():
    return "SHIN-" + "-".join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))

def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎯 Buy 1 Days"), KeyboardButton("🎯 Buy 3 Days")],
        [KeyboardButton("🎯 Buy 7 Days"), KeyboardButton("🎯 Buy 15 Days")],
        [KeyboardButton("🎯 Buy 30 Days"), KeyboardButton("📦 Stock")],
        [KeyboardButton("➕ Add Funds"), KeyboardButton("💰 Balance")],
        [KeyboardButton("📁 My Purchases")]
    ], resize_keyboard=True)

def get_game_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("🃏 CARROM")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)

def get_confirm_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("✅ Confirm")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)

def get_user(uid):
    if uid not in USERS:
        USERS[uid] = {"balance": 0.0, "total": 0.0, "purchases": []}
    return USERS[uid]

async def start(update, context):
    context.user_data.clear()
    u = get_user(update.effective_user.id)
    name = update.effective_user.first_name
    text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🏅 Plan: Bronze\n💰 Balance: ₹{u['balance']:.2f}\n🇮🇳 Country: India\n\n🚀 Select an option below to get started:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

async def handle_message(update, context):
    msg = update.message.text
    uid = update.effective_user.id
    user = get_user(uid)

    if msg == "💰 Balance":
        await update.message.reply_text(f"💰 Balance: ₹{user['balance']:.2f}\n📊 Total Funded: ₹{user['total']:.2f}", reply_markup=get_main_menu())
        return

    if msg == "📦 Stock":
        await update.message.reply_text(f"📦 Stock: CARROM - {STOCK.get('CARROM',0)} keys available", reply_markup=get_main_menu())
        return

    if msg == "➕ Add Funds":
        # Demo: 40 taka add hoye jabe - tumi chaile QR dite paro
        user['balance'] += 40
        user['total'] += 40
        await update.message.reply_text(f"🎉 Payment Successful!\n\n💰 Amount: ₹40.0\n💰 Balance: ₹{user['balance']:.2f}\n📊 Total Funded: ₹{user['total']:.2f}", reply_markup=get_main_menu())
        return

    if "Buy" in msg and "Days" in msg:
        for plan in PRICES:
            if plan in msg:
                context.user_data['plan'] = plan
                await update.message.reply_text(f"🎁 {plan} Plan Selected")
                await update.message.reply_text("🎮 Select a Game:", reply_markup=get_game_menu())
                return

    if "CARROM" in msg.upper():
        plan = context.user_data.get('plan',"1 Days")
        price = VIP_PRICES.get(plan, 40)
        stock = STOCK.get("CARROM",0)
        context.user_data['price_val'] = price
        text = f"🛒 Confirm Purchase\n\n🎯 Game: CARROM\n⏰ Duration: {plan}\n💰 Price: ₹{price:.2f} (👑 Vip pricing)\n📦 Stock: {stock} keys available\n\n👉 Tap ✅ Confirm to proceed or ❌ Cancel to abort."
        await update.message.reply_text(text, reply_markup=get_confirm_menu())
        return

    if msg == "✅ Confirm" or msg.lower() == "confirm":
        plan = context.user_data.get('plan')
        price = context.user_data.get('price_val',0)
        if not plan:
            await update.message.reply_text("❌ No plan selected", reply_markup=get_main_menu())
            return
        if STOCK.get("CARROM",0) <= 0:
            await update.message.reply_text("❌ Out of Stock!", reply_markup=get_main_menu())
            return
        if user['balance'] < price:
            await update.message.reply_text(f"❌ Insufficient Balance! Need ₹{price}, you have ₹{user['balance']}", reply_markup=get_main_menu())
            return
        user['balance'] -= price
        STOCK["CARROM"] -= 1
        key = gen_key()
        user['purchases'].append(key)
        await update.message.reply_text(f"✅ Purchase Successful!\n\n🎯 Game: CARROM\n⏰ Duration: {plan}\n💰 Paid: ₹{price:.2f} (👑 Vip pricing)\n💰 Remaining Balance: ₹{user['balance']:.2f}\n\n🔑 Your Key:\n{key}\n\n💡 Use 📁 My Purchases to view history!", reply_markup=get_main_menu())
        await update.message.reply_text("📋 Back to main menu:", reply_markup=get_main_menu())
        return

    if "Cancel" in msg or msg == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled", reply_markup=get_main_menu())
        await start(update, context)
        return

    if "My Purchases" in msg:
        keys = "\n".join(user['purchases'][-5:]) or "No purchases yet"
        await update.message.reply_text(f"📁 Your Keys:\n{keys}", reply_markup=get_main_menu())

def main():
    threading.Thread(target=run_flask).start()
    app_b = Application.builder().token(BOT_TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_b.run_polling()

if __name__ == "__main__":
    main()
