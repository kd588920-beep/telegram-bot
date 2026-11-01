import json,os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,ContextTypes
BOT_TOKEN=os.getenv("BOT_TOKEN")
DB="database.json"
def load():
 try:
  with open(DB) as f: return json.load(f)
 except: return {}
def save(d):
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
  await update.message.reply_text(f"👑 Welcome Back to SHINIGAMI Bot!\n👤 Name: {update.effective_user.first_name}\n💰 Balance: ₹{db[u].get('balance',0)}\n🌍 Country: {db[u]['country']}\n\n🚀 Select an option:",reply_markup=kb())
  await update.message.reply_text("Menu cleared ✅",reply_markup=ReplyKeyboardRemove())
 else:
  k=[[InlineKeyboardButton("🇮🇳 INDIA",callback_data="in")],[InlineKeyboardButton("🇧🇩 BD",callback_data="bd")]]
  await update.message.reply_text("Select country:",reply_markup=InlineKeyboardMarkup(k))
async def country(update,context):
 q=update.callback_query
 u=str(q.from_user.id)
 db=load()
 if u not in db: db[u]={"balance":0}
 db[u]["country"]="India" if q.data=="in" else "Bangladesh"
 save(db)
 await q.answer()
 await q.edit_message_text(f"👑 Welcome\n🌍 {db[u]['country']}\n\n🚀 Select:",reply_markup=kb())
async def btn(update,context):
 q=update.callback_query
 b=load().get(str(q.from_user.id),{}).get("balance",0)
 await q.answer()
 if q.data=="stock": await q.message.reply_text("📦 Stock: 125 Accounts ✅")
 elif q.data=="balance": await q.message.reply_text(f"💰 Balance: ₹{b}")
 elif q.data=="addfund": await q.message.reply_text("💸 Add Funds:\nUPI: tomar@okaxis\nbKash: 01XXX")
 elif q.data=="getfiles": await q.message.reply_text("📂 Get Files: Age plan keno!")
 else: await q.message.reply_text("🛒 Balance lagbe!")
def run():
 app=Application.builder().token(BOT_TOKEN).build()
 app.add_handler(CommandHandler("start",start))
 app.add_handler(CallbackQueryHandler(country,pattern="^(in|bd)$"))
 app.add_handler(CallbackQueryHandler(btn,pattern="^(buy1|buy3|buy7|buy15|buy30|stock|addfund|balance|getfiles)$"))
 app.run_polling()
if __name__=="__main__": run()
