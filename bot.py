import os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,filters,ContextTypes

BOT_TOKEN=os.getenv("BOT_TOKEN")
DB={}  # Memory te thakbe, file lagbe na

def main_kb():
    return ReplyKeyboardMarkup([
        ["🔥 Buy 1 Days","🔥 Buy 3 Days"],
        ["🔥 Buy 7 Days","🔥 Buy 15 Days"],
        ["🔥 Buy 30 Days","📦 Stock"],
        ["➕ Add Funds","💰 Balance"],
        ["📂 Get Files"]], resize_keyboard=True)

def inline_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Buy 1 Days",callback_data="buy1"),InlineKeyboardButton("🔥 Buy 3 Days",callback_data="buy3")],
        [InlineKeyboardButton("🔥 Buy 7 Days",callback_data="buy7"),InlineKeyboardButton("🔥 Buy 15 Days",callback_data="buy15")],
        [InlineKeyboardButton("🔥 Buy 30 Days",callback_data="buy30"),InlineKeyboardButton("📦 Stock",callback_data="stock")],
        [InlineKeyboardButton("➕ Add Funds",callback_data="addfund"),InlineKeyboardButton("💰 Balance",callback_data="balance")],
        [InlineKeyboardButton("📂 Get Files",callback_data="getfiles")]])

async def start(update,context):
    u=str(update.effective_user.id)
    if u in DB and "country" in DB[u]:
        await update.message.reply_text(f"👑 Welcome Back!\n👤 {update.effective_user.first_name}\n💰 ₹{DB[u].get('balance',0)}\n🌍 {DB[u]['country']}\n\n🚀 Select:", reply_markup=main_kb())
    else:
        k=[[InlineKeyboardButton("🇮🇳 INDIA - UPI",callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH - bKash/Nagad",callback_data="bd")]]
        await update.message.reply_text("Please select your country to continue:", reply_markup=InlineKeyboardMarkup(k))

async def country(update,context):
    q=update.callback_query
    u=str(q.from_user.id)
    await q.answer()
    if u not in DB: DB[u]={"balance":0,"plan":"Bronze"}
    if u=="7189081595": DB[u]["plan"]="ADMIN - Boss"
    DB[u]["country"]="India" if q.data=="in" else "Bangladesh"
    await q.edit_message_text(f"✅ Country set to {DB[u]['country']} ✅\n\nEbar /start dao, ar country chaibe na!")
    await context.bot.send_message(chat_id=q.message.chat_id, text=f"👑 Welcome!\n🌍 {DB[u]['country']}\n💰 Balance: ₹{DB[u]['balance']}", reply_markup=main_kb())

async def buttons(update,context):
    q=update.callback_query
    if q:
        await q.answer()
        d=q.data
        bal=DB.get(str(q.from_user.id),{}).get("balance",0)
        if d=="stock": await q.message.reply_text("📦 Stock: 125 Accounts ✅")
        elif d=="balance": await q.message.reply_text(f"💰 Balance: ₹{bal}")
        elif d=="addfund": await q.message.reply_text("💸 Add Funds:\nUPI: tomar@okaxis")
        elif d=="getfiles": await q.message.reply_text("📂 Get Files: Age plan keno!")
        else: await q.message.reply_text("🛒 Buy korte Balance lagbe!")
    else:
        txt=update.message.text
        uid=str(update.effective_user.id)
        bal=DB.get(uid,{}).get("balance",0)
        if "Stock" in txt: await update.message.reply_text("📦 Stock: 125 Accounts ✅")
        elif "Balance" in txt: await update.message.reply_text(f"💰 Balance: ₹{bal}")
        elif "Add Funds" in txt: await update.message.reply_text("💸 UPI: tomar@okaxis\nbKash: 01XXX")
        elif "Get Files" in txt: await update.message.reply_text("📂 Age plan keno!")
        elif "Buy" in txt: await update.message.reply_text("🛒 Buy korte Add Funds koro!")

def run():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CallbackQueryHandler(country,pattern="^(in|bd)$"))
    app.add_handler(CallbackQueryHandler(buttons,pattern="^(buy1|buy3|buy7|buy15|buy30|stock|addfund|balance|getfiles)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.run_polling()

if __name__=="__main__": run()
