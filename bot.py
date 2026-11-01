import os
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

VIP_PRICES = {"1 Days":40,"3 Days":100,"7 Days":150,"15 Days":300,"30 Days":500}
KEYS = []
USERS = {}

def get_main_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("🎯 Buy 1 Days"),KeyboardButton("🎯 Buy 3 Days")],[KeyboardButton("🎯 Buy 7 Days"),KeyboardButton("🎯 Buy 15 Days")],[KeyboardButton("🎯 Buy 30 Days"),KeyboardButton("📦 Stock")],[KeyboardButton("➕ Add Funds"),KeyboardButton("💰 Balance")],[KeyboardButton("📁 My Purchases")]], resize_keyboard=True)
def get_game_menu(): return ReplyKeyboardMarkup([[KeyboardButton("🃏 CARROM")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_confirm_menu(): return ReplyKeyboardMarkup([[KeyboardButton("✅ Confirm")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_admin_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("👑 Add Keys"),KeyboardButton("📦 Stock")],[KeyboardButton("👥 Stats"),KeyboardButton("🔙 User Menu")]], resize_keyboard=True)
def get_user(uid):
    if uid not in USERS: USERS[uid] = {"balance": 0.0, "purchases": []}
    return USERS[uid]

async def start(update, context):
    context.user_data.clear()
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"👑 Welcome to SHINIGAMI Bot!\n💰 Balance: ₹{u['balance']:.2f}\n📦 Stock: {len(KEYS)} keys", reply_markup=get_main_menu())

async def admin(update, context):
    if update.effective_user.id != ADMIN_ID: 
        await update.message.reply_text("❌ You are not admin!"); return
    await update.message.reply_text(f"👑 ADMIN PANEL\n📦 Stock: {len(KEYS)} keys\n👥 Users: {len(USERS)}", reply_markup=get_admin_menu())

async def handle_message(update, context):
    msg = update.message.text; uid = update.effective_user.id; user = get_user(uid)
    if uid == ADMIN_ID:
        if msg == "📦 Stock" and context.user_data.get('in_admin'): await update.message.reply_text(f"📦 Stock: {len(KEYS)}\n{KEYS[:10]}", reply_markup=get_admin_menu()); return
        if msg == "👥 Stats": await update.message.reply_text(f"👥 Users: {len(USERS)}\n📦 Stock: {len(KEYS)}", reply_markup=get_admin_menu()); return
        if msg == "🔙 User Menu": context.user_data['in_admin']=False; await start(update, context); return
        if msg == "👑 Add Keys":
            context.user_data['admin_mode']="addkey"; context.user_data['in_admin']=True
            await update.message.reply_text("🔑 Key paste koro (1 line = 1 key):"); return
        if context.user_data.get('admin_mode')=="addkey":
            new_keys=[k.strip() for k in msg.split("\n") if k.strip()]
            KEYS.extend(new_keys)
            await update.message.reply_text(f"✅ {len(new_keys)} keys added! Total: {len(KEYS)}", reply_markup=get_admin_menu())
            context.user_data['admin_mode']=None; return

    if msg == "📦 Stock": await update.message.reply_text(f"📦 Stock: {len(KEYS)} keys", reply_markup=get_main_menu()); return
    if msg == "💰 Balance": await update.message.reply_text(f"💰 Balance: ₹{user['balance']:.2f}", reply_markup=get_main_menu()); return
    if msg == "➕ Add Funds": user['balance']+=40; await update.message.reply_text(f"✅ ₹40 Added", reply_markup=get_main_menu()); return
    if "Buy" in msg:
        for p in VIP_PRICES:
            if p in msg: context.user_data['plan']=p; await update.message.reply_text(f"🎁 {p} Selected", reply_markup=get_game_menu()); return
    if "CARROM" in msg.upper():
        plan=context.user_data.get('plan',"1 Days"); price=VIP_PRICES.get(plan,40)
        context.user_data['price_val']=price
        await update.message.reply_text(f"🛒 Confirm\n{plan} - ₹{price}\nStock: {len(KEYS)}\nTap ✅ Confirm", reply_markup=get_confirm_menu()); return
    if msg == "✅ Confirm":
        price=context.user_data.get('price_val',0)
        if len(KEYS)<=0: await update.message.reply_text("❌ Out of Stock!", reply_markup=get_main_menu()); return
        if user['balance']<price: await update.message.reply_text(f"❌ Need ₹{price}", reply_markup=get_main_menu()); return
        user['balance']-=price; key=KEYS.pop(0); user['purchases'].append(key)
        await update.message.reply_text(f"✅ Success!\n🔑 Key: {key}\n📦 Left: {len(KEYS)}", reply_markup=get_main_menu()); return
    if "Cancel" in msg: await start(update, context); return

def main():
    threading.Thread(target=run_flask).start()
    app_b = Application.builder().token(BOT_TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(CommandHandler("admin", admin))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_b.run_polling()
if __name__ == "__main__": main()
