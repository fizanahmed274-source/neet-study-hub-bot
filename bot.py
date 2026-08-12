import os
import json
import random
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    BOT_TOKEN,
    CHANNEL_USERNAME,
    GROUP_USERNAME,
    CHANNEL_URL,
    GROUP_URL,
    BOT_NAME,
)

from database import (
    init_database,
    add_user,
    update_score,
    get_user,
    get_leaderboard,
)

from ai import ask_ai


# =========================================================
# FILE LOADERS
# =========================================================

def load_chapters():
    with open("chapters.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_questions():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)["questions"]


# =========================================================
# FORCE JOIN
# =========================================================

async def is_member(user_id, context):

    try:
        channel = await context.bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        group = await context.bot.get_chat_member(
            GROUP_USERNAME,
            user_id
        )

        allowed = [
            "member",
            "administrator",
            "creator"
        ]

        return (
            channel.status in allowed
            and group.status in allowed
        )

    except Exception:
        return False


async def force_join_message(message):

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_URL
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Join Group",
                url=GROUP_URL
            )
        ],
        [
            InlineKeyboardButton(
                "✅ I Have Joined",
                callback_data="verify_join"
            )
        ],
    ]

    await message.reply_text(
        "🔐 Join Required\n\n"
        "NEET Study Hub use karne ke liye pehle "
        "hamara Channel aur Group join karo.\n\n"
        "1️⃣ Channel join karo\n"
        "2️⃣ Group join karo\n"
        "3️⃣ I Have Joined dabao 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )

    if not await is_member(user.id, context):
        await force_join_message(update.message)
        return

    await main_menu(update.message)


# =========================================================
# MAIN MENU
# =========================================================

async def main_menu(message):

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Practice",
                callback_data="practice"
            ),
            InlineKeyboardButton(
                "📝 PYQ",
                callback_data="pyq"
            )
        ],
        [
            InlineKeyboardButton(
                "🎯 Mock Test",
                callback_data="mock"
            ),
            InlineKeyboardButton(
                "🤖 AI Doubt",
                callback_data="ai"
            )
        ],
        [
            InlineKeyboardButton(
                "🫀 3D Biology",
                callback_data="biology"
            )
        ],
        [
            InlineKeyboardButton(
                "🔥 Daily Challenge",
                callback_data="daily"
            ),
            InlineKeyboardButton(
                "🏆 Leaderboard",
                callback_data="leaderboard"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 My Progress",
                callback_data="progress"
            )
        ],
        [
            InlineKeyboardButton(
                "❤️ Support",
                callback_data="support"
            )
        ],
    ]

    await message.reply_text(
        f"🧠 {BOT_NAME}\n\n"
        "Apna option choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# PRACTICE MENU
# =========================================================

async def practice_menu(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "⚡ Physics",
                callback_data="subject_Physics"
            )
        ],
        [
            InlineKeyboardButton(
                "🧪 Chemistry",
                callback_data="subject_Chemistry"
            )
        ],
        [
            InlineKeyboardButton(
                "🧬 Biology",
                callback_data="subject_Biology"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home"
            )
        ],
    ]

    await query.message.edit_text(
        "📚 Practice Mode\n\n"
        "Subject choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# CLASS MENU
# =========================================================

async def class_menu(query, subject):

    keyboard = [
        [
            InlineKeyboardButton(
                "📘 Class 11",
                callback_data=f"class_11_{subject}"
            )
        ],
        [
            InlineKeyboardButton(
                "📕 Class 12",
                callback_data=f"class_12_{subject}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="practice"
            )
        ],
    ]

    await query.message.edit_text(
        f"📚 {subject}\n\n"
        "Class choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# CHAPTER MENU
# =========================================================

async def chapter_menu(query, class_number, subject):

    chapters = load_chapters()

    chapter_list = (
        chapters
        .get(str(class_number), {})
        .get(subject, [])
    )

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
                callback_data=(
                    f"chapter|{class_number}|"
                    f"{subject}|{index}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Back",
            callback_data=f"subject_{subject}"
        )
    ])

    await query.message.edit_text(
        f"📚 Class {class_number} {subject}\n\n"
        "Chapter choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# PRACTICE QUESTIONS
# =========================================================

async def start_question(
    query,
    class_number,
    subject,
    chapter
):

    questions = load_questions()

    matching = [
        q for q in questions
        if str(q.get("class")) == str(class_number)
        and q.get("subject") == subject
        and q.get("chapter") == chapter
    ]

    if not matching:

        await query.message.edit_text(
            "📚 Is chapter ke questions abhi add nahi hue.\n\n"
            "🔥 Question bank next stage mein add kiya jayega."
        )
        return

    question = random.choice(matching)

    options = question["options"]

    keyboard = []

    for index, option in enumerate(options):

        keyboard.append([
            InlineKeyboardButton(
                f"{chr(65 + index)}) {option}",
                callback_data=(
                    f"answer|{question['id']}|{index}"
                )
            )
        ])

    text = (
        f"🔥 {question.get('difficulty', 'NEET Level')}\n\n"
        f"🧠 {question['question']}\n\n"
        "Answer choose karo 👇"
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# ANSWER
# =========================================================

async def answer_question(
    query,
    question_id,
    option_index
):

    questions = load_questions()

    question = next(
        (
            q for q in questions
            if str(q["id"]) == str(question_id)
        ),
        None
    )

    if not question:

        await query.answer(
            "Question nahi mila.",
            show_alert=True
        )
        return

    selected = question["options"][option_index]

    correct = (
        selected == question["answer"]
    )

    update_score(
        query.from_user.id,
        correct
    )

    if correct:

        result = "✅ Correct Answer!"

    else:

        result = (
            "❌ Wrong Answer!\n\n"
            f"✅ Correct: {question['answer']}"
        )

    text = (
        f"{result}\n\n"
        "💡 Explanation:\n"
        f"{question['explanation']}"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Practice Menu",
                callback_data="practice"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )
        ]
    ]

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# AI DOUBT
# =========================================================

async def ai_doubt_start(query, context):

    context.user_data["waiting_for_ai"] = True

    await query.message.edit_text(
        "🤖 AI Doubt Solver\n\n"
        "Apna NEET doubt message mein bhejo.\n\n"
        "Example:\n"
        "Why does increasing temperature affect equilibrium?\n\n"
        "❌ /cancel se AI mode band kar sakte ho."
    )


async def ai_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.user_data.get(
        "waiting_for_ai",
        False
    ):
        return

    user = update.effective_user

    # Force join check
    if not await is_member(
        user.id,
        context
    ):

        context.user_data[
            "waiting_for_ai"
        ] = False

        await force_join_message(
            update.message
        )

        return

    question = update.message.text.strip()

    if question == "/cancel":

        context.user_data[
            "waiting_for_ai"
        ] = False

        await update.message.reply_text(
            "❌ AI Doubt mode closed."
        )

        return

    if not question:

        await update.message.reply_text(
            "⚠️ Apna doubt text mein bhejo."
        )

        return

    # Turn off waiting state
    context.user_data[
        "waiting_for_ai"
    ] = False

    waiting_message = await update.message.reply_text(
        "🤔 Doubt solve kar raha hoon..."
    )

    try:

        # Run AI without blocking Telegram
        answer = await asyncio.to_thread(
            ask_ai,
            question
        )

        await waiting_message.edit_text(
            "🤖 AI Answer\n\n" + answer
        )

    except Exception as error:

        print("AI ERROR:", error)

        await waiting_message.edit_text(
            "⚠️ AI service abhi available nahi hai.\n\n"
            "Thodi der baad dobara try karo."
        )


# =========================================================
# PROGRESS
# =========================================================

async def show_progress(query):

    user = get_user(
        query.from_user.id
    )

    if not user:

        await query.message.edit_text(
            "No progress found."
        )

        return

    score = user[3]
    attempted = user[4]
    correct = user[5]

    await query.message.edit_text(
        "📊 My Progress\n\n"
        f"🎯 Score: {score}\n"
        f"📝 Attempted: {attempted}\n"
        f"✅ Correct: {correct}\n"
    )


# =========================================================
# LEADERBOARD
# =========================================================

async def show_leaderboard(query):

    users = get_leaderboard(10)

    if not users:

        await query.message.edit_text(
            "🏆 Leaderboard abhi empty hai."
        )

        return

    text = "🏆 TOP 10 NEET STUDENTS\n\n"

    for position, user in enumerate(
        users,
        start=1
    ):

        username = user[1] or "Student"
        score = user[2]

        text += (
            f"{position}. {username} — "
            f"{score} points\n"
        )

    await query.message.edit_text(
        text
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # -------------------------
    # VERIFY JOIN
    # -------------------------

    if data == "verify_join":

        if await is_member(
            query.from_user.id,
            context
        ):

            await query.message.edit_text(
                "🎉 Verification Successful!\n\n"
                "Welcome to NEET Study Hub 2027 ❤️"
            )

            await main_menu(
                query.message
            )

        else:

            await query.answer(
                "❌ Pehle Channel aur Group dono join karo!",
                show_alert=True
            )

    # -------------------------
    # HOME
    # -------------------------

    elif data == "home":

        context.user_data[
            "waiting_for_ai"
        ] = False

        await main_menu(
            query.message
        )

    # -------------------------
    # PRACTICE
    # -------------------------

    elif data == "practice":

        await practice_menu(
            query
        )

    # -------------------------
    # SUBJECT
    # -------------------------

    elif data.startswith(
        "subject_"
    ):

        subject = data.replace(
            "subject_",
            ""
        )

        await class_menu(
            query,
            subject
        )

    # -------------------------
    # CLASS
    # -------------------------

    elif data.startswith(
        "class_"
    ):

        parts = data.split(
            "_",
            2
        )

        class_number = parts[1]
        subject = parts[2]

        await chapter_menu(
            query,
            class_number,
            subject
        )

    # -------------------------
    # CHAPTER
    # -------------------------

    elif data.startswith(
        "chapter|"
    ):

        parts = data.split("|")

        class_number = parts[1]
        subject = parts[2]
        chapter_index = int(parts[3])

        chapters = load_chapters()

        chapter = (
            chapters
            [str(class_number)]
            [subject]
            [chapter_index]
        )

        await start_question(
            query,
            class_number,
            subject,
            chapter
        )

    # -------------------------
    # ANSWER
    # -------------------------

    elif data.startswith(
        "answer|"
    ):

        parts = data.split("|")

        question_id = parts[1]
        option_index = int(parts[2])

        await answer_question(
            query,
            question_id,
            option_index
        )

    # -------------------------
    # AI
    # -------------------------

    elif data == "ai":

        await ai_doubt_start(
            query,
            context
        )

    # -------------------------
    # PROGRESS
    # -------------------------

    elif data == "progress":

        await show_progress(
            query
        )

    # -------------------------
    # LEADERBOARD
    # -------------------------

    elif data == "leaderboard":

        await show_leaderboard(
            query
        )

    # -------------------------
    # FUTURE FEATURES
    # -------------------------

    elif data in [
        "pyq",
        "mock",
        "biology",
        "daily",
        "support"
    ]:

        await query.message.edit_text(
            "🚧 Ye feature development mein hai.\n\n"
            "Jald hi available hoga 🔥"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        raise ValueError(
            "BOT_TOKEN missing!"
        )

    init_database()

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Buttons
    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Normal text messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_message
        )
    )

    print(
        f"{BOT_NAME} started..."
    )

    application.run_polling()


# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":
    main()
