import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595  # Tomar ID bosiye dilam
DB_FILE = "users.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["🔥 Buy 1 Days", "🔥 Buy 3 Days"],
        ["🔥 Buy 7 Days", "🔥 Buy 15 Days"],
        ["🔥 Buy 30 Days", "📦 Stock"],
        ["➕ Add Funds", "💰 Balance"],
        ["📁 Get Files"]
    ], resize_keyboard=True)

# Tumi jake VIP banabe
async def makevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Tumi admin na!")
        return
    if not context.args: 
        await update.message.reply_text("Use: /makevip USER_ID\nExample: /makevip 123456789")
        return
    uid = context.args[0]
    db = load_db()
    if uid not in db: db[uid] = {"balance":0, "plan":"Free User", "country":"India"}
    db[uid]["plan"] = "Vip 🔥 VIP/Reseller"
    save_db(db)
    await update.message.reply_text(f"✅ {uid} ke VIP banano holo!")

async def removevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id
