import os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,filters

BOT_TOKEN=os.getenv("BOT_TOKEN")
DB={}

def main_kb():
    return ReplyKeyboardMarkup([
        ["🔥 Buy 1 Days","🔥 Buy 3 Days"],
        ["🔥 Buy 7 Days","🔥 Buy 15 Days"],
        ["🔥 Buy 30 Days","📦 Stock"],
        ["➕ Add Funds","💰 Balance"],
        ["📂 Get Files"]], resize_keyboard=True)

async def start(update,context):
    u=str(update.effective_user.id)
    if u in DB and "country" in DB[u]:
        await update.message.reply_text(f"👑 Welcome Back!\n🌍 {DB[u]['country']}\n💰 ₹{DB[u].get('balance',0)}", reply_markup=main_kb())
    else:
        k=[[InlineKeyboardButton("🇮🇳 INDIA - UPI",callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH",callback_data="bd")]]
        await update.message.reply_text("Please select your country:", reply_markup=InlineKeyboardMarkup(k))

async def country(update,context):
    q=update.callback_query
    u=str(q.from_user.id)
    await q.answer()
    if u not in DB: DB[u]={"balance":0,"plan":"Bronze"}
    if u=="7189081595": DB[u]["plan"]="ADMIN - Boss"
    DB[u]["country"]="India" if q.data=="in" else "Bangladesh"
    await q.edit_message_text(f"✅ Country set to {DB[u]['country']}")
    await context.bot.send_message(chat_id=q.message.chat_id, text=f"👑 Welcome! Use menu below:", reply_markup=main_kb())

async def buttons(update,context):
    q=update.callback_query
    if q:
        await q.answer()
        if q.data=="stock": await q.message.reply_text("📦 Stock: 125 Accounts ✅")
        elif q.data=="balance": 
            bal=DB.get(str(q.from_user.id),{}).get("balance",0)
            await q.message.reply_text(f"💰 Balance: ₹{bal}")
        else: await q.message.reply_text("🛒 Add Funds koro!")
    else:
        txt=update.message.text
        bal=DB.get(str(update.effective_user.id),{}).get("balance",0)
        if "Stock" in txt: await update.message.reply_text("📦 Stock: 125 Accounts ✅")
        elif "Balance" in txt: await update.message.reply_text(f"💰 Balance: ₹{bal}")
        else: await update.message.reply_text("🛒 Buy korte Add Funds koro!")

def run():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CallbackQueryHandler(country,pattern="^(in|bd)$"))
    app.add_handler(CallbackQueryHandler(buttons,pattern="^(buy1|buy3|buy7|buy15|buy30|stock|addfund|balance|getfiles)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.run_polling()

if __name__=="__main__": run()
