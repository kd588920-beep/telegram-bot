import os, random, string
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7189081595
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹190","15 Days":"₹350","30 Days":"₹570"}
VIP_PRICES = {"1 Days":40,"3 Days":100,"7 Days":150,"15 Days":300,"30 Days":500}
KEYS = []  # EKHANE ASOL KEY THAKBE
USERS = {}

def get_main_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("🎯 Buy 1 Days"),KeyboardButton("🎯 Buy 3 Days")],[KeyboardButton("🎯 Buy 7 Days"),KeyboardButton("🎯 Buy 15 Days")],[KeyboardButton("🎯 Buy 30 Days"),KeyboardButton("📦 Stock")],[KeyboardButton("➕ Add Funds"),KeyboardButton("💰 Balance")],[KeyboardButton("📁 My Purchases")]], resize_keyboard=True)
def get_game_menu(): return ReplyKeyboardMarkup([[KeyboardButton("🃏 CARROM")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_confirm_menu(): return ReplyKeyboardMarkup([[KeyboardButton("✅ Confirm")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_admin_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("👑 Add Keys"),KeyboardButton("📦 Stock")],[KeyboardButton("👥 Stats"),KeyboardButton("🔙 User Menu")]], resize_keyboard=True)
def get_user(uid):
    if uid not in USERS: USERS[uid] = {"balance": 0.0, "total": 0.0, "purchases": []}
    return USERS[uid]

async def start(update, context):
    context.user_data.clear()
    u = get_user(update.effective_user.id)
    text = f"👑 Welcome to SHINIGAMI Bot!\n💰 Balance: ₹{u['balance']:.2f}\n📦 Stock: {len(KEYS)} keys\n\nSelect an option:"
    await update.message.reply_text(text, reply_markup=get_main_menu())
async def prices(update, context):
    await update.message.reply_text(f"💰 Price List - Stock: {len(KEYS)} keys\n• 1 Day ₹70 (VIP ₹40)\n• 3 Days ₹140 (VIP ₹100)\n• 7 Days ₹190 (VIP ₹150)\n• 15 Days ₹350 (VIP ₹300)\n• 30 Days ₹570 (VIP ₹500)")
async def support(update, context):
    await update.message.reply_text("📞 Support: @Koushikgaming")
async def admin(update, context):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(f"👑 ADMIN PANEL\n📦 Real Stock: {len(KEYS)} keys\n👥 Users: {len(USERS)}\n\n👑 Add Keys e click kore key paste koro, auto add hobe!", reply_markup=get_admin_menu())

async def handle_message(update, context):
    msg = update.message.text; uid = update.effective_user.id; user = get_user(uid)
    if uid == ADMIN_ID:
        if msg == "📦 Stock": await update.message.reply_text(f"📦 Real Stock: {len(KEYS)} keys\n{KEYS[:5]}", reply_markup=get_admin_menu()); return
        if msg == "👥 Stats": await update.message.reply_text(f"👥 {len(USERS)} users\n📦 {len(KEYS)} keys in stock", reply_markup=get_admin_menu()); return
        if msg == "🔙 User Menu": await start(update, context); return
        if msg == "👑 Add Keys":
            context.user_data['admin_mode'] = "addkey"
            await update.message.reply_text("🔑 Key gulo paste koro (1 line e 1 ta key)\nExample:\nCARROM-1234\nCARROM-5678"); return
        if context.user_data.get('admin_mode') == "addkey" and len(msg) > 3:
            new_keys = [k.strip() for k in msg.split("\n") if k.strip()!=""]
            KEYS.extend(new_keys)
            await update.message.reply_text(f"✅ {len(new_keys)} ta key add holo!\n📦 Total Stock: {len(KEYS)} keys", reply_markup=get_admin_menu())
            context.user_data['admin_mode']=None; return

    if msg == "💰 Balance": await update.message.reply_text(f"💰 Balance: ₹{user['balance']:.2f}", reply_markup=get_main_menu()); return
    if msg == "📦 Stock": await update.message.reply_text(f"📦 Stock: {len(KEYS)} keys available", reply_markup=get_main_menu()); return
    if msg == "➕ Add Funds": user['balance']+=40; await update.message.reply_text(f"✅ ₹40 Added! Balance: ₹{user['balance']}", reply_markup=get_main_menu()); return
    if "Buy" in msg and "Days" in msg:
        for plan in PRICES:
            if plan in msg:
                context.user_data['plan']=plan
                await update.message.reply_text(f"🎁 {plan} Selected\n🎮 Select Game:", reply_markup=get_game_menu()); return
    if "CARROM" in msg.upper():
        plan=context.user_data.get('plan',"1 Days"); price=VIP_PRICES.get(plan,40)
        context.user_data['price_val']=price
        await update.message.reply_text(f"🛒 Confirm\nGame: CARROM\nDuration: {plan}\nPrice: ₹{price}\nStock: {len(KEYS)} keys\nTap ✅ Confirm", reply_markup=get_confirm_menu()); return
    if msg == "✅ Confirm":
        plan=context.user_data.get('plan'); price=context.user_data.get('price_val',0)
        if len(KEYS)<=0: await update.message.reply_text("❌ Out of Stock! Admin ke bolo key add korte", reply_markup=get_main_menu()); return
        if user['balance']<price: await update.message.reply_text(f"❌ Need ₹{price}, you have ₹{user['balance']}", reply_markup=get_main_menu()); return
        user['balance']-=price; key=KEYS.pop(0); user['purchases'].append(key)
        await update.message.reply_text(f"✅ Purchase Successful!\n\n🔑 Key:\n{key}\n💰 Balance: ₹{user['balance']}\n📦 Remaining Stock: {len(KEYS)}", reply_markup=get_main_menu()); return
    if "Cancel" in msg: await start(update, context); return

def main():
    threading.Thread(target=run_flask).start()
    app_b = Application.builder().token(BOT_TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(CommandHandler("prices", prices))
    app_b.add_handler(CommandHandler("support", support))
    app_b.add_handler(CommandHandler("admin", admin))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_b.run_polling()
if __name__ == "__main__": main()
