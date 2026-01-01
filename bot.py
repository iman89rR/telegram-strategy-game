print("BOT IS STARTING...")
from config import BOT_TOKEN
print("TOKEN CHECK:", BOT_TOKEN)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN
from database import init_db, get_db


# ───────────── منوی اصلی ─────────────
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏛 کشور من", callback_data="my_country")],
        [InlineKeyboardButton("🌍 جهان", callback_data="world")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("📌 منوی اصلی:", reply_markup=markup)
    else:
        await update.callback_query.edit_message_text(
            "📌 منوی اصلی:",
            reply_markup=markup
        )


# ───────────── /start ─────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user.id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user.id, user.username)
        )
        cur.execute(
            """INSERT INTO countries
               (user_id, name, money, military, factories)
               VALUES (?, ?, ?, ?, ?)""",
            (user.id, f"Country of {user.first_name}", 1000, 100, 1)
        )
        conn.commit()
        await update.message.reply_text("🎉 کشورت ساخته شد!")

    conn.close()
    await main_menu(update, context)


# ───────────── کشور من ─────────────
async def my_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT name, money, military, factories FROM countries WHERE user_id = ?",
        (user_id,)
    )
    country = cur.fetchone()
    conn.close()

    if not country:
        await query.edit_message_text("❌ کشوری پیدا نشد.")
        return

    name, money, military, factories = country

    text = (
        f"🏛 **{name}**\n\n"
        f"💰 پول: {money}\n"
        f"⚔️ ارتش: {military}\n"
        f"🏭 کارخانه: {factories}"
    )

    keyboard = [[InlineKeyboardButton("⬅️ بازگشت", callback_data="menu")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ───────────── Callback ها ─────────────
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "menu":
        await main_menu(update, context)
    elif data == "my_country":
        await my_country(update, context)
    elif data == "world":
        await update.callback_query.edit_message_text("🌍 جهان (در حال ساخت)")


# ───────────── اجرای بات ─────────────
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
