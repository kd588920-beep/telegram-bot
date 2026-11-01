import json,os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,ContextTypes
BOT_TOKEN=os.getenv("BOT_TOKEN")
DB="database.json"

# Memory te DB rakhbo - bar bar country chaibe na
DB_CACHE={}
def load():
    global DB_CACHE
    if DB_CACHE: return DB_CACHE
    try:
        with open(DB) as f: DB_CACHE=json.load(f)
        return DB_CACHE
    except: return {}
def save(d):
    global DB_CACHE
    DB_CACHE=d
    with open(DB,"w") as f: json.dump(d,f)

def kb():
 return InlineKeyboardMarkup([
  [InlineKeyboardButton("🔥 Buy 1 Days",callback_data="buy1"),InlineKeyboardButton("🔥 Buy 3 Days",callback_data="buy3")],
  [InlineKeyboardButton("🔥 Buy 7 Days",callback_data="buy7"),InlineKeyboardButton("🔥 Buy 15 Days",callback_data="buy15")],
  [InlineKeyboardButton("🔥 Buy 30 Days",callback_data="buy30"),InlineKeyboardButton("📦 Stock",callback_data="stock")],
  [InlineKeyboardButton("➕ Add Funds",callback_data="addfund"),InlineKeyboardButton("💰 Balance",callback_data="balance")],
  [InlineKeyboardButton("📂 Get Files",callback_data="getfiles")]])

async def start(update,context):
 u=str(update.effective_user.id)
 db=load()
 if u in db and "country" in db[u]:
  await update.message.reply_text(f"👑 Welcome Back!\n👤 {update.effective_user.first_name}\n👑 {db[u].get('plan','USER')}\n💰 ₹{db[u].get('balance',0)}\n🌍 {db[u]['country']}\n\n🚀 Select:",reply_markup=kb(),disable_web_page_preview=True)
 else:
  k=[[InlineKeyboardButton("🇮🇳 INDIA - UPI",callback_data="in")],[InlineKeyboardButton("🇧🇩 BANGLADESH",callback_data="bd")]]
  await update.message.reply_text("Please select your country to continue:",reply_markup=InlineKeyboardMarkup(k))

async def country(update,context):
 q=update.callback_query
 u=str(q.from_user.id)
 db=load()
 if u not in db: db[u]={"balance":0,"plan":"Bronze"}
 db[u]["country"]="India" if q.data=="in" else "Bangladesh"
 if u=="7189081595" or q.from_user.username=="koushik": db[u]["plan"]="ADMIN - Boss"
 save(db)
 await q.answer()
 # Purono white keyboard delete + notun green keyboard pathabo
 await context.bot.send_message(chat_id=q.message.chat_id,text="✅ Country Saved!",reply_markup=ReplyKeyboardRemove())
 await context.bot.send_message(chat_id=q.message.chat_id,text=f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {q.from_user.first_name}\n🏅 Plan: {db[u]['plan']}\n💰 Balance: ₹{db[u]['balance']}\n🌍 Country: {db[u]['country']}\n\n🚀 Select an option below:",reply_markup=kb())

async def btn(update,context):
 q=update.callback_query
 b=load().get(str(q.from_user.id),{}).get("balance",0)
 await q.answer()
 if q.data=="stock": await q.message.reply_text("📦 Stock: 125 Accounts ✅")
 elif q.data=="balance": await q.message.reply_text(f"💰 Balance: ₹{b}")
 elif q.data=="addfund": await q.message.reply_text("💸 Add Funds:\nUPI: tomar@okaxis")
 elif q.data=="getfiles": await q.message.reply_text("📂 Get Files: Age plan keno!")
 else: await q.message.reply_text("🛒 Balance lagbe!")

def run():
 app=Application.builder().token(BOT_TOKEN).build()
 app.add_handler(CommandHandler("start",start))
 app.add_handler(CallbackQueryHandler(country,pattern="^(in|bd)$"))
 app.add_handler(CallbackQueryHandler(btn,pattern="^(buy1|buy3|buy7|buy15|buy30|stock|addfund|balance|getfiles)$"))
 app.run_polling()
if __name__=="__main__": run()
