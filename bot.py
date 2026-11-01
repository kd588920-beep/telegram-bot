import json
from telebot import TeleBot, types

BOT_TOKEN = "TOMAR_BOT_TOKEN_EKHANE_DAO"
ADMIN_ID = 123456789 # Tomar Telegram ID

bot = TeleBot(BOT_TOKEN)

# Alada Stock Database
STOCK_FILE = "stock.json"
try:
    with open(STOCK_FILE, 'r') as f:
        stock = json.load(f)
except:
    stock = {"1D": [], "3D": [], "7D": [], "15D": [], "30D": []}

def save_stock():
    with open(STOCK_FILE, 'w') as f:
        json.dump(stock, f)

def get_stock_text():
    return f"""📦 **Total Stock:**
1 Days: {len(stock['1D'])} keys
3 Days: {len(stock['3D'])} keys
7 Days: {len(stock['7D'])} keys
15 Days: {len(stock['15D'])} keys
30 Days: {len(stock['30D'])} keys
Total: {sum(len(v) for v in stock.values())} keys"""

# Admin Panel
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("1D Add", callback_data="add_1D"),
        types.InlineKeyboardButton("3D Add", callback_data="add_3D"),
        types.InlineKeyboardButton("7D Add", callback_data="add_7D"),
        types.InlineKeyboardButton("15D Add", callback_data="add_15D"),
        types.InlineKeyboardButton("30D Add", callback_data="add_30D"),
    )
    bot.send_message(message.chat.id, get_stock_text() + "\n\nKonta add korbe?", reply_markup=markup, parse_mode="Markdown")

# Add Key Logic
user_state = {}
@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def ask_keys(call):
    plan = call.data.split("_")[1] # 1D, 3D etc
    user_state[call.from_user.id] = plan
    bot.send_message(call.message.chat.id, f"🔑 **{plan} er key paste koro (1 line = 1 key):**\n\nNiche paste kore send koro.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in user_state)
def save_keys(message):
    plan = user_state.pop(message.from_user.id)
    keys = [k.strip() for k in message.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    save_stock()
    bot.send_message(message.chat.id, f"✅ {len(keys)} ta key {plan} e add holo!\n\n{get_stock_text()}", parse_mode="Markdown")

bot.polling()
