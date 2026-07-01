import random
import sqlite3
import time
from typing import Any, Optional, Set, Tuple


GRID_SIZE = 32
MOVE_DURATION_SEC = 0.8

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
def random_free_cell(extra_occupied = None, conn = None, ) -> Tuple[int, int]:
    """
    Возвращает случайную свободную клетку на поле.

    :param extra_occupied: клетка занятая монеткой
    :param conn: соединение с БД для чтения позиций игроков
    :raises ValueError: если свободных клеток нет
    """
    # 1. Собираем клетки занятые котами
    occupied = get_occupied_cells(conn)

    # 2. Добавляем клетку с монеткой
    if extra_occupied:
        occupied.add(extra_occupied)

    # 3. Создаём список всех свободных клеток
    all_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
    free_cells = [cell for cell in all_cells if cell not in occupied]

    # 4. Проверяем, есть ли свободные клетки
    if not free_cells:
        raise RuntimeError("Игровое поле заполнено!")

    # 5. Выбираем случайную клетку
    return random.choice(free_cells)

def get_occupied_cells(conn, exclude_id = None) -> Set[Tuple[int, int]]:
    """Собирает клетки, занятые котами."""
    occupied = set()
    rows = conn.execute("SELECT telegram_id, cell_x, cell_y FROM players").fetchall()
    for row in rows:
        if exclude_id is not None and row["telegram_id"] == exclude_id:
            continue
        occupied.add((row["cell_x"], row["cell_y"]))
    return occupied

def join_player(telegram_id: int, username: str, conn: sqlite3.Connection) -> dict[str, Any]:
    """
    Регистрирует игрока или возвращает существующего.

    :raises ValueError: no_free_cells
    """
    existing = conn.execute(
        "SELECT telegram_id, cell_x, cell_y FROM players WHERE telegram_id = ?",
        (telegram_id,),
    ).fetchone()
    if existing is not None:
        return {
            "status": "already_joined",
            "telegram_id": telegram_id,
            "cell_x": existing["cell_x"],
            "cell_y": existing["cell_y"],
        }

    coin_row = conn.execute("SELECT coin_x, coin_y FROM game_state WHERE id = 1").fetchone()

    extra = set()
    if coin_row is not None:
        extra.add((coin_row["coin_x"], coin_row["coin_y"]))
    cell_x, cell_y = random_free_cell(extra_occupied=extra, conn=conn)
    conn.execute(
        """
        INSERT INTO players (
            telegram_id, username, cell_x, cell_y, joined_at,
            coins_collected, moving_until
        ) VALUES (?, ?, ?, ?, ?, 0, 0)
        """,
        (telegram_id, username, cell_x, cell_y, time.time()),
    )
    conn.commit()
    return {
        "status": "created",
        "telegram_id": telegram_id,
        "cell_x": cell_x,
        "cell_y": cell_y,
    }

def move_player(telegram_id: int, direction: str, conn: sqlite3.Connection) -> dict[str, Any]:
    """
    Перемещает кота на одну клетку.

    :raises ValueError: коды ошибок still_moving, out_of_bounds, cell_occupied, not_found
    """
    if direction not in DIRECTIONS:
        raise ValueError("invalid_direction")

    player = conn.execute(
        "SELECT * FROM players WHERE telegram_id = ?",
        (telegram_id,),
    ).fetchone()
    if player is None:
        raise ValueError("not_found")

    # А если ещё перемещается?

    dx, dy = DIRECTIONS[direction]
    new_x = player["cell_x"] + dx
    new_y = player["cell_y"] + dy

    if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE:
        raise ValueError("out_of_bounds")

    occupied = get_occupied_cells(conn, exclude_id=telegram_id)
    if (new_x, new_y) in occupied:
        raise ValueError("cell_occupied")

    coin_row = conn.execute("SELECT coin_x, coin_y FROM game_state WHERE id = 1").fetchone()
    coin_picked = coin_row["coin_x"] == new_x and coin_row["coin_y"] == new_y
    new_coins = player["coins_collected"] + (1 if coin_picked else 0)
    moving_until = time.time() + MOVE_DURATION_SEC

    conn.execute(
        """
        UPDATE players
        SET cell_x = ?, cell_y = ?, coins_collected = ?, moving_until = ?
        WHERE telegram_id = ?
        """,
        (new_x, new_y, new_coins, moving_until, telegram_id),
    )

    if coin_picked:
        try:
            coin_x, coin_y = random_free_cell(conn=conn)
        except ValueError:
            coin_x, coin_y = 0, 0
        conn.execute(
            "UPDATE game_state SET coin_x = ?, coin_y = ? WHERE id = 1",
            (coin_x, coin_y),
        )

    conn.commit()
    return {
        "status": "moved",
        "cell_x": new_x,
        "cell_y": new_y,
        "coins_collected": new_coins,
        "coin_picked": coin_picked,
    }