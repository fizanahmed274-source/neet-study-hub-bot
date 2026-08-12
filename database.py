import sqlite3

DATABASE = "neet_bot.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            score INTEGER DEFAULT 0,
            questions_attempted INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            daily_questions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_user(user_id, username, first_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username, first_name))

    connection.commit()
    connection.close()


def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def update_score(user_id, correct):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET
            questions_attempted = questions_attempted + 1,
            correct_answers = correct_answers + ?,
            score = score + ?
        WHERE user_id = ?
    """, (
        1 if correct else 0,
        4 if correct else 0,
        user_id
    ))

    connection.commit()
    connection.close()


def get_leaderboard(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, username, score
        FROM users
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))

    users = cursor.fetchall()

    connection.close()

    return users
