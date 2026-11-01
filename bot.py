import os, random, string
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7189081595  # TUMI ADMIN

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live"
def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

PRICES = {"1 Days":"₹70","3 Days":"₹140","7 Days":"₹190","15 Days":"₹350","30 Days":"₹570"}
VIP_PRICES = {"1 Days":40,"3 Days":100,"7 Days":150,"15 Days":300,"30 Days":500}
STOCK = {"CARROM": 5}
USERS = {}

def gen_key(): return "SHIN-" + "-".join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
def get_main_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("🎯 Buy 1 Days"),KeyboardButton("🎯 Buy 3 Days")],[KeyboardButton("🎯 Buy 7 Days"),KeyboardButton("🎯 Buy 15 Days")],[KeyboardButton("🎯 Buy 30 Days"),KeyboardButton("📦 Stock")],[KeyboardButton("➕ Add Funds"),KeyboardButton("💰 Balance")],[KeyboardButton("📁 My Purchases")]], resize_keyboard=True)
def get_game_menu(): return ReplyKeyboardMarkup([[KeyboardButton("🃏 CARROM")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_confirm_menu(): return ReplyKeyboardMarkup([[KeyboardButton("✅ Confirm")],[KeyboardButton("❌ Cancel")]], resize_keyboard=True)
def get_admin_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("👑 Add Stock"),KeyboardButton("💸 Add Balance")],[KeyboardButton("👥 Stats"),KeyboardButton("🔙 User Menu")]], resize_keyboard=True)
def get_user(uid):
    if uid not in USERS: USERS[uid] = {"balance": 0.0, "total": 0.0, "purchases": [], "name": ""}
    return USERS[uid]

async def start(update, context):
    context.user_data.clear()
    u = get_user(update.effective_user.id)
    u['name'] = update.effective_user.first_name
    text = f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {u['name']}\n🏅 Plan: {'Admin 👑' if update.effective_user.id==ADMIN_ID else 'Bronze'}\n💰 Balance: ₹{u['balance']:.2f}\n🇮🇳 Country: India\n\n🚀 Select an option below:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

async def prices(update, context):
    await update.message.reply_text("💰 Price List:\n\n🎯 CARROM\n• 1 Day = ₹70 (VIP ₹40)\n• 3 Days = ₹140 (VIP ₹100)\n• 7 Days = ₹190 (VIP ₹150)\n• 15 Days = ₹350 (VIP ₹300)\n• 30 Days = ₹570 (VIP ₹500)")

async def support(update, context):
    await update.message.reply_text("📞 Support: @Koushikgaming")

async def admin(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not admin!"); return
    await update.message.reply_text(f"👑 ADMIN PANEL\n\n👥 Users: {len(USERS)}\n📦 Stock: {STOCK['CARROM']}\n\nCommands:\n• Add Stock - likho: 10\n• Add Balance - UserID Amount\nExample: 7189081595 100", reply_markup=get_admin_menu())

async def handle_message(update, context):
    msg = update.message.text
    uid = update.effective_user.id
    user = get_user(uid)
    user['name'] = update.effective_user.first_name

    # ADMIN LOGIC
    if uid == ADMIN_ID:
        if msg == "👥 Stats":
            await update.message.reply_text(f"👥 Total Users: {len(USERS)}\n📦 Stock: {STOCK['CARROM']}\n" + "\n".join([f"{k} - ₹{v['balance']}" for k,v in list(USERS.items())[:10]])); return
        if msg == "🔙 User Menu":
            await start(update, context); return
        if msg == "👑 Add Stock":
            context.user_data['admin_mode'] = "stock"
            await update.message.reply_text("📦 Koto stock add korbe? Number likho - Jemon: 10"); return
        if msg == "💸 Add Balance":
            context.user_data['admin_mode'] = "balance"
            await update.message.reply_text("💸 Format: USER_ID AMOUNT\nJemon: 123456789 100"); return
        if context.user_data.get('admin_mode') == "stock" and msg.isdigit():
            STOCK["CARROM"] += int(msg)
            await update.message.reply_text(f"✅ Stock Added! New Stock: {STOCK['CARROM']}", reply_markup=get_admin_menu()); context.user_data['admin_mode']=None; return
        if context.user_data.get('admin_mode') == "balance":
            try:
                parts = msg.split()
                tid = int(parts[0]); amt = float(parts[1])
                tu = get_user(tid); tu['balance']+=amt; tu['total']+=amt
                await update.message.reply_text(f"✅ Added ₹{amt} to {tid}\nNew Balance: ₹{tu['balance']}", reply_markup=get_admin_menu())
                context.user_data['admin_mode']=None; return
            except: pass

    # USER LOGIC
    if msg == "💰 Balance":
        await update.message.reply_text(f"💰 Balance: ₹{user['balance']:.2f}\n📊 Total: ₹{user['total']:.2f}", reply_markup=get_main_menu()); return
    if msg == "📦 Stock":
        await update.message.reply_text(f"📦 Stock: CARROM - {STOCK.get('CARROM',0)} keys", reply_markup=get_main_menu()); return
    if msg == "➕ Add Funds":
        user['balance'] += 40; user['total'] += 40
        await update.message.reply_text(f"🎉 Payment Successful!\n💰 Amount: ₹40.0\n💰 Balance: ₹{user['balance']:.2f}", reply_markup=get_main_menu()); return
    if "Buy" in msg and "Days" in msg:
        for plan in PRICES:
            if plan in msg:
                context.user_data['plan'] = plan
                await update.message.reply_text(f"🎁 {plan} Plan Selected"); await update.message.reply_text("🎮 Select a Game:", reply_markup=get_game_menu()); return
    if "CARROM" in msg.upper():
        plan = context.user_data.get('plan',"1 Days"); price = VIP_PRICES.get(plan, 40); stock = STOCK.get("CARROM",0)
        context.user_data['price_val'] = price
        await update.message.reply_text(f"🛒 Confirm Purchase\n\n🎯 Game: CARROM\n⏰ Duration: {plan}\n💰 Price: ₹{price:.2f} (👑 Vip)\n📦 Stock: {stock} keys\n\n👉 Tap ✅ Confirm", reply_markup=get_confirm_menu()); return
    if msg == "✅ Confirm":
        plan = context.user_data.get('plan'); price = context.user_data.get('price_val',0)
        if STOCK.get("CARROM",0) <= 0: await update.message.reply_text("❌ Out of Stock!", reply_markup=get_main_menu()); return
        if user['balance'] < price: await update.message.reply_text(f"❌ Need ₹{price}, you have ₹{user['balance']}", reply_markup=get_main_menu()); return
        user['balance'] -= price; STOCK["CARROM"] -= 1; key = gen_key(); user['purchases'].append(key)
        await update.message.reply_text(f"✅ Purchase Successful!\n\n🎯 CARROM\n⏰ {plan}\n💰 Paid: ₹{price:.2f}\n💰 Balance: ₹{user['balance']:.2f}\n\n🔑 Key:\n{key}", reply_markup=get_main_menu()); return
    if "Cancel" in msg:
        await update.message.reply_text("❌ Cancelled", reply_markup=get_main_menu()); await start(update, context); return
    if "My Purchases" in msg:
        keys = "\n".join(user['purchases'][-5:]) or "No purchases yet"
        await update.message.reply_text(f"📁 Your Keys:\n{keys}", reply_markup=get_main_menu())

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
