import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")
GROUP_URL = os.getenv("GROUP_URL", "https://t.me/your_group")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 Join Group", url=GROUP_URL)],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🧠 *Welcome to NEET Study Hub 2027!*\n\n"
        "📚 Your complete NEET study companion.\n\n"
        "To use the bot, first join our official Channel and Group.\n\n"
        "👇 Join both and then tap *I Have Joined*.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "⏳ Membership verification system is being prepared.\n\n"
        "Once the bot is fully configured, your membership will be checked automatically."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("NEET Study Hub Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
