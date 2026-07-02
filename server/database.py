import os
import sqlite3

import game_logic

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "game.db"),
)


def get_connection() -> sqlite3.Connection:
    """Открывает соединение с базой данных."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Создаёт таблицы players и game_state, если их ещё нет."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                cell_x INTEGER NOT NULL CHECK (cell_x >= 0 AND cell_x < 32),
                cell_y INTEGER NOT NULL CHECK (cell_y >= 0 AND cell_y < 32),
                joined_at REAL NOT NULL,
                coins_collected INTEGER NOT NULL DEFAULT 0,
                moving_until REAL NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                coin_x INTEGER NOT NULL CHECK (coin_x >= 0 AND coin_x < 32),
                coin_y INTEGER NOT NULL CHECK (coin_y >= 0 AND coin_y < 32)
            );
            """)
        row = conn.execute("SELECT id FROM game_state WHERE id = 1").fetchone()
        if row is None:
            coin_x, coin_y = game_logic.random_free_cell(conn=conn)
            conn.execute(
                "INSERT INTO game_state (id, coin_x, coin_y) VALUES (1, ?, ?)",
                (coin_x, coin_y),
            )
        conn.commit()
    finally:
        conn.close()
