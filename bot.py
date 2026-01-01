# bot.py
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3

# ✅ توکن از Environment Variable خوانده می‌شود
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# -------- Database helpers --------
DB_FILE = "game.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # جدول کاربران
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)
    # جدول کشورها
    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        money INTEGER,
        military INTEGER,
        factories INTEGER
    )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    return conn

# -------- Bot Handlers --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
    exists = cur.fetchone()

    if exists:
        await update.message.reply_text("🏛 تو قبلاً کشورت رو ساختی!")
    else:
        # ایجاد کاربر و کشور
        cur.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
        cur.execute(
            "INSERT INTO countries (user_id, name, money, military, factories) VALUES (?, ?, ?, ?, ?)",
            (user.id, f"Country of {user.first_name}", 1000, 100, 1)
        )
        conn.commit()
        await update.message.reply_text(
            "🎉 کشورت با موفقیت ساخته شد!\n💰 پول: 1000\n⚔️ ارتش: 100\n🏭 کارخانه: 1"
        )
    conn.close()

    # نمایش منوی اصلی
    await main_menu(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏛 کشور من", callback_data="my_country")],
        [InlineKeyboardButton("🌍 جهان", callback_data="world")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("📌 منوی اصلی:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("📌 منوی اصلی:", reply_markup=reply_markup)

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "menu":
        await main_menu(update, context)
    elif data == "my_country":
        await my_country(update, context)
    elif data == "world":
        await world(update, context)

async def my_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, money, military, factories FROM countries WHERE user_id = ?", (user_id,))
    country = cur.fetchone()
    conn.close()

    if not country:
        await query.edit_message_text("❌ کشوری پیدا نشد.")
        return

    name, money, military, factories = country
    text = f"🏛 **{name}**\n\n💰 پول: {money}\n⚔️ ارتش: {military}\n🏭 کارخانه: {factories}"

    keyboard = [[InlineKeyboardButton("⬅️ بازگشت", callback_data="menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def world(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "🌍 جهان هنوز ساده است. بعداً اضافه می‌کنیم!"
    keyboard = [[InlineKeyboardButton("⬅️ بازگشت", callback_data="menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# -------- Main --------
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
