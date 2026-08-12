import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@Neetmastry"
GROUP = "@neetmastery0"

CHANNEL_URL = "https://t.me/Neetmastry"
GROUP_URL = "https://t.me/neetmastery0"


async def check_membership(user_id, context):
    try:
        channel = await context.bot.get_chat_member(CHANNEL, user_id)
        group = await context.bot.get_chat_member(GROUP, user_id)

        valid_status = ["member", "administrator", "creator"]

        return (
            channel.status in valid_status
            and group.status in valid_status
        )

    except Exception:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    joined = await check_membership(user_id, context)

    if joined:
        await show_main_menu(update)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 Join Group", url=GROUP_URL)],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")],
    ]

    await update.message.reply_text(
        "🧠 *Welcome to NEET Study Hub 2027!*\n\n"
        "Bot use karne ke liye pehle hamara Channel aur Group join karo.\n\n"
        "1️⃣ Channel join karo\n"
        "2️⃣ Group join karo\n"
        "3️⃣ Phir *I Have Joined* dabao 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    joined = await check_membership(user_id, context)

    if joined:
        await query.message.edit_text(
            "🎉 *Verification Successful!*\n\n"
            "Welcome to NEET Study Hub 2027 ❤️",
            parse_mode="Markdown",
        )

        await show_main_menu(query.message)

    else:
        await query.answer(
            "❌ Pehle Channel aur Group dono join karo!",
            show_alert=True,
        )


async def show_main_menu(message):

    keyboard = [
        [
            InlineKeyboardButton("📚 Practice", callback_data="practice"),
            InlineKeyboardButton("📝 PYQ", callback_data="pyq"),
        ],
        [
            InlineKeyboardButton("🎯 Mock Test", callback_data="mock"),
            InlineKeyboardButton("🤖 AI Doubt", callback_data="ai"),
        ],
        [
            InlineKeyboardButton("🫀 3D Biology", callback_data="biology"),
        ],
        [
            InlineKeyboardButton("🔥 Daily Challenge", callback_data="daily"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton("📊 My Progress", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("❤️ Support", callback_data="support"),
        ],
    ]

    await message.reply_text(
        "🏠 *NEET Study Hub 2027*\n\n"
        "Apna option choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🚧 Ye feature abhi development mein hai.\n\n"
        "Jald hi available hoga ❤️"
    )


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("NEET Study Hub Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
