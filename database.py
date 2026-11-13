import sqlite3
from pathlib import Path

from flask import current_app, g

def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE"]

        Path(db_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db

def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        users_count = db.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        if users_count == 0:

            db.executemany(
                "INSERT INTO users (username) VALUES (?)",
                [
                    ("demo_user",),
                    ("student",)
                ]
            )

            db.executemany(
                """
                INSERT INTO listings
                (user_id, title, description)
                VALUES (?, ?, ?)
                """,
                [
                    (
                        1,
                        "Продам ноутбук",
                        "Ноутбук в хорошем состоянии. "
                        "Подходит для учёбы и работы."
                    ),
                    (
                        1,
                        "Куплю монитор",
                        "Ищу монитор с диагональю от 24 дюймов."
                    ),
                    (
                        2,
                        "Отдам книги",
                        "Отдам учебники по программированию."
                    )
                ]
            )

            db.execute(
                """
                INSERT INTO comments
                (listing_id, user_id, content)
                VALUES (?, ?, ?)
                """,
                (
                    1,
                    2,
                    "Здравствуйте! Объявление ещё актуально?"
                )
            )

        db.commit()