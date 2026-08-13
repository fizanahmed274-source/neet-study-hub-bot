import os
import json
import random
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

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
# LOAD FILES
# =========================================================

def load_chapters():
    with open("chapters.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_questions():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)["questions"]


# =========================================================
# KEYBOARDS
# =========================================================

def home_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )
        ]
    ])


def back_home_keyboard(back_callback):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data=back_callback
            ),
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )
        ]
    ])


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

    except Exception as error:
        print("JOIN CHECK ERROR:", error)
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

    context.user_data["waiting_for_ai"] = False

    add_user(
        user.id,
        user.username,
        user.first_name
    )

    if not await is_member(user.id, context):
        await force_join_message(update.message)
        return

    await main_menu(update.message, edit=False)


# =========================================================
# MAIN MENU
# =========================================================

async def main_menu(message, edit=False):

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

    text = (
        f"🧠 {BOT_NAME}\n\n"
        "Apna option choose karo 👇"
    )

    markup = InlineKeyboardMarkup(keyboard)

    if edit:
        await message.edit_text(
            text,
            reply_markup=markup
        )
    else:
        await message.reply_text(
            text,
            reply_markup=markup
        )


# =========================================================
# PRACTICE SUBJECT
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
            ),
            InlineKeyboardButton(
                "🏠 Home",
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
            ),
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
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
            "⚠️ Is class ke chapters available nahi hain.",
            reply_markup=back_home_keyboard(
                f"subject_{subject}"
            )
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
        ),
        InlineKeyboardButton(
            "🏠 Home",
            callback_data="home"
        )
    ])

    await query.message.edit_text(
        f"📚 Class {class_number} {subject}\n\n"
        "Chapter choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================================================
# QUESTION
# =========================================================

async def start_question(
    query,
    class_number,
    subject,
    chapter,
    chapter_index
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
            "📚 Is chapter ke questions abhi add nahi hue.",
            reply_markup=back_home_keyboard(
                f"class_{class_number}_{subject}"
            )
        )

        return

    question = random.choice(matching)

    keyboard = []

    for index, option in enumerate(question["options"]):

        keyboard.append([
            InlineKeyboardButton(
                f"{chr(65 + index)}) {option}",
                callback_data=(
                    f"answer|{question['id']}|{index}|"
                    f"{class_number}|{subject}|{chapter_index}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Back",
            callback_data=(
                f"class_{class_number}_{subject}"
            )
        ),
        InlineKeyboardButton(
            "🏠 Home",
            callback_data="home"
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
    option_index,
    class_number,
    subject,
    chapter_index
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

    if option_index < 0 or option_index >= len(question["options"]):

        await query.answer(
            "Invalid option.",
            show_alert=True
        )

        return

    selected = question["options"][option_index]

    correct = selected == question["answer"]

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
                "🔄 More Questions",
                callback_data=(
                    f"chapter|{class_number}|"
                    f"{subject}|{chapter_index}"
                )
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data=(
                    f"class_{class_number}_{subject}"
                )
            ),
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
# AI
# =========================================================

async def ai_doubt_start(query, context):

    context.user_data["waiting_for_ai"] = True

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home"
            ),
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )
        ]
    ]

    await query.message.edit_text(
        "🤖 AI Doubt Solver\n\n"
        "Apna NEET doubt message mein bhejo.\n\n"
        "Example:\n"
        "Why does increasing temperature affect equilibrium?\n\n"
        "❌ /cancel se AI mode band kar sakte ho.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def ai_message(update, context):

    if not context.user_data.get(
        "waiting_for_ai",
        False
    ):
        return

    user = update.effective_user

    if not await is_member(
        user.id,
        context
    ):

        context.user_data["waiting_for_ai"] = False

        await force_join_message(update.message)

        return

    question = update.message.text.strip()

    if question == "/cancel":

        context.user_data["waiting_for_ai"] = False

        await update.message.reply_text(
            "❌ AI mode closed.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home"
                    )
                ]
            ])
        )

        return

    if not question:

        await update.message.reply_text(
            "⚠️ Apna doubt text mein bhejo."
        )

        return

    context.user_data["waiting_for_ai"] = False

    waiting = await update.message.reply_text(
        "🤔 Doubt solve kar raha hoon..."
    )

    try:

        answer = await asyncio.to_thread(
            ask_ai,
            question
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🤖 Ask Another",
                    callback_data="ai"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="home"
                ),
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="home"
                )
            ]
        ]

        await waiting.edit_text(
            "🤖 AI Answer\n\n" + answer,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as error:

        print("AI ERROR:", error)

        await waiting.edit_text(
            "⚠️ AI service abhi available nahi hai.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🤖 Try Again",
                        callback_data="ai"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="home"
                    ),
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home"
                    )
                ]
            ])
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
            "📊 My Progress\n\n"
            "Abhi koi progress record nahi hai.",
            reply_markup=home_keyboard()
        )

        return

    score = user[3]
    attempted = user[4]
    correct = user[5]

    await query.message.edit_text(
        "📊 My Progress\n\n"
        f"🎯 Score: {score}\n"
        f"📝 Attempted: {attempted}\n"
        f"✅ Correct: {correct}\n",
        reply_markup=back_home_keyboard("home")
    )


# =========================================================
# LEADERBOARD
# =========================================================

async def show_leaderboard(query):

    users = get_leaderboard(10)

    if not users:

        await query.message.edit_text(
            "🏆 Leaderboard abhi empty hai.",
            reply_markup=back_home_keyboard("home")
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
        text,
        reply_markup=back_home_keyboard("home")
    )


# =========================================================
# FUTURE FEATURE
# =========================================================

async def future_feature(query, title):

    await query.message.edit_text(
        f"{title}\n\n"
        "🚧 Ye feature development mein hai.\n\n"
        "Jald hi available hoga 🔥",
        reply_markup=back_home_keyboard("home")
    )


# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(update, context):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================================================
    # HOME
    # =====================================================

    if data == "home":

        context.user_data["waiting_for_ai"] = False

        await main_menu(
            query.message,
            edit=True
        )

    # =====================================================
    # VERIFY JOIN
    # =====================================================

    elif data == "verify_join":

        if await is_member(
            query.from_user.id,
            context
        ):

            context.user_data["waiting_for_ai"] = False

            await query.message.edit_text(
                "🎉 Verification Successful!\n\n"
                "Welcome to NEET Study Hub 2027 ❤️"
            )

            await main_menu(
                query.message,
                edit=True
            )

        else:

            await query.answer(
                "❌ Pehle Channel aur Group dono join karo!",
                show_alert=True
            )

    # =====================================================
    # PRACTICE
    # =====================================================

    elif data == "practice":

        context.user_data["waiting_for_ai"] = False

        await practice_menu(query)

    # =====================================================
    # SUBJECT
    # =====================================================

    elif data.startswith("subject_"):

        subject = data.replace(
            "subject_",
            ""
        )

        await class_menu(
            query,
            subject
        )

    # =====================================================
    # CLASS
    # =====================================================

    elif data.startswith("class_"):

        parts = data.split("_", 2)

        if len(parts) != 3:
            await query.answer(
                "Invalid class.",
                show_alert=True
            )
            return

        class_number = parts[1]
        subject = parts[2]

        await chapter_menu(
            query,
            class_number,
            subject
        )

    # =====================================================
    # CHAPTER
    # =====================================================

    elif data.startswith("chapter|"):

        parts = data.split("|")

        if len(parts) != 4:
            await query.answer(
                "Invalid chapter.",
                show_alert=True
            )
            return

        class_number = parts[1]
        subject = parts[2]
        chapter_index = int(parts[3])

        chapters = load_chapters()

        chapter = (
            chapters
            .get(str(class_number), {})
            .get(subject, [])
        )

        if chapter_index >= len(chapter):

            await query.answer(
                "Chapter nahi mila.",
                show_alert=True
            )

            return

        selected_chapter = chapter[chapter_index]

        await start_question(
            query,
            class_number,
            subject,
            selected_chapter,
            chapter_index
        )

    # =====================================================
    # ANSWER
    # =====================================================

    elif data.startswith("answer|"):

        parts = data.split("|")

        if len(parts) != 6:
            await query.answer(
                "Invalid answer.",
                show_alert=True
            )
            return

        question_id = parts[1]
        option_index = int(parts[2])
        class_number = parts[3]
        subject = parts[4]
        chapter_index = int(parts[5])

        await answer_question(
            query,
            question_id,
            option_index,
            class_number,
            subject,
            chapter_index
        )

    # =====================================================
    # AI
    # =====================================================

    elif data == "ai":

        await ai_doubt_start(
            query,
            context
        )

    # =====================================================
    # PROGRESS
    # =====================================================

    elif data == "progress":

        await show_progress(query)

    # =====================================================
    # LEADERBOARD
    # =====================================================

    elif data == "leaderboard":

        await show_leaderboard(query)

    # =====================================================
    # FUTURE FEATURES
    # =====================================================

    elif data == "pyq":

        await future_feature(
            query,
            "📝 NEET PYQ"
        )

    elif data == "mock":

        await future_feature(
            query,
            "🎯 Mock Test"
        )

    elif data == "biology":

        await future_feature(
            query,
            "🫀 3D Biology"
        )

    elif data == "daily":

        await future_feature(
            query,
            "🔥 Daily Challenge"
        )

    elif data == "support":

        await future_feature(
            query,
            "❤️ Support"
        )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):

    print(
        "BOT ERROR:",
        context.error
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

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_message
        )
    )

    application.add_error_handler(
        error_handler
    )

    print(
        f"{BOT_NAME} started..."
    )

    application.run_polling()


if __name__ == "__main__":
    main()
