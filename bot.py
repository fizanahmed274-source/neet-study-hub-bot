import os
import json

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


# ---------- LOAD CHAPTERS ----------

def load_chapters():
    with open("chapters.json", "r", encoding="utf-8") as file:
        return json.load(file)


# ---------- FORCE JOIN ----------

async def check_membership(user_id, context):
    try:
        channel = await context.bot.get_chat_member(CHANNEL, user_id)
        group = await context.bot.get_chat_member(GROUP, user_id)

        valid = ["member", "administrator", "creator"]

        return (
            channel.status in valid
            and group.status in valid
        )

    except Exception:
        return False


# ---------- START ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if await check_membership(user_id, context):
        await show_main_menu(update.message)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 Join Group", url=GROUP_URL)],
        [InlineKeyboardButton(
            "✅ I Have Joined",
            callback_data="check_join"
        )],
    ]

    await update.message.reply_text(
        "🧠 *Welcome to NEET Study Hub 2027!*\n\n"
        "Bot use karne ke liye pehle Channel aur Group join karo.\n\n"
        "1️⃣ Channel join karo\n"
        "2️⃣ Group join karo\n"
        "3️⃣ I Have Joined dabao 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ---------- JOIN CHECK ----------

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await check_membership(user_id, context):

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


# ---------- MAIN MENU ----------

async def show_main_menu(message):

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Practice",
                callback_data="practice"
            ),
            InlineKeyboardButton(
                "📝 PYQ",
                callback_data="pyq"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎯 Mock Test",
                callback_data="mock"
            ),
            InlineKeyboardButton(
                "🤖 AI Doubt",
                callback_data="ai"
            ),
        ],
        [
            InlineKeyboardButton(
                "🫀 3D Biology",
                callback_data="biology"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔥 Daily Challenge",
                callback_data="daily"
            ),
            InlineKeyboardButton(
                "🏆 Leaderboard",
                callback_data="leaderboard"
            ),
        ],
        [
            InlineKeyboardButton(
                "📊 My Progress",
                callback_data="progress"
            ),
        ],
        [
            InlineKeyboardButton(
                "❤️ Support",
                callback_data="support"
            ),
        ],
    ]

    await message.reply_text(
        "🏠 *NEET Study Hub 2027*\n\n"
        "Apna option choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ---------- PRACTICE SUBJECT ----------

async def practice_menu(query):

    keyboard = [
        [InlineKeyboardButton(
            "⚡ Physics",
            callback_data="subject_Physics"
        )],
        [InlineKeyboardButton(
            "🧪 Chemistry",
            callback_data="subject_Chemistry"
        )],
        [InlineKeyboardButton(
            "🧬 Biology",
            callback_data="subject_Biology"
        )],
        [InlineKeyboardButton(
            "🔙 Back",
            callback_data="back_home"
        )],
    ]

    await query.message.edit_text(
        "📚 *Practice Mode*\n\n"
        "Subject choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ---------- CLASS MENU ----------

async def class_menu(query, subject):

    keyboard = [
        [InlineKeyboardButton(
            "📘 Class 11",
            callback_data=f"class_11_{subject}"
        )],
        [InlineKeyboardButton(
            "📕 Class 12",
            callback_data=f"class_12_{subject}"
        )],
        [InlineKeyboardButton(
            "🔙 Back",
            callback_data="practice"
        )],
    ]

    await query.message.edit_text(
        f"📚 *{subject} Practice*\n\n"
        "Class choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ---------- CHAPTER MENU ----------

async def chapter_menu(query, class_num, subject):

    chapters = load_chapters()

    chapter_list = chapters.get(str(class_num), {}).get(subject, [])

    if not chapter_list:
        await query.message.edit_text(
            "⚠️ Is class ke chapters abhi available nahi hain."
        )
        return

    keyboard = []

    for index, chapter in enumerate(chapter_list):
        keyboard.append([
            InlineKeyboardButton(
                f"📖 {chapter}",
                callback_data=f"chapter_{class_num}_{subject}_{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Back",
            callback_data=f"subject_{subject}"
        )
    ])

    await query.message.edit_text(
        f"📚 *Class {class_num} {subject}*\n\n"
        "Chapter choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ---------- BUTTON HANDLER ----------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "check_join":
        await check_join(update, context)

    elif data == "practice":
        await practice_menu(query)

    elif data.startswith("subject_"):
        subject = data.replace("subject_", "")
        await class_menu(query, subject)

    elif data.startswith("class_"):

        parts = data.split("_", 2)

        class_num = parts[1]
        subject = parts[2]

        await chapter_menu(
            query,
            class_num,
            subject
        )

    elif data.startswith("chapter_"):

        await query.message.edit_text(
            "🔥 *Chapter selected!*\n\n"
            "Question system next step mein connect hoga.\n"
            "Tough NEET-level questions ready honge 💪",
            parse_mode="Markdown",
        )

    elif data == "back_home":
        await show_main_menu(query.message)

    else:
        await query.message.reply_text(
            "🚧 Ye feature abhi development mein hai."
        )


# ---------- RUN ----------

def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("NEET Study Hub Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
