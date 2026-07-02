import time
import requests
import config
from cat import Cat

WIDTH = HEIGHT = config.W
TITLE = "Cats"

cats_by_player_id = {}
coin_cell = (0, 0)
last_poll_time = 0.0


def fetch_game_state():
    """Load players and coin position from Flask server."""
    global coin_cell
    try:
        response = requests.get(f"{config.SERVER}/api/game/state", timeout=2)
        game_data = response.json()
    except Exception:
        return

    coin_cell = (game_data["coin"]["cell_x"], game_data["coin"]["cell_y"])
    active_player_ids = set()

    for player in game_data["players"]:
        player_id = player["telegram_id"]
        active_player_ids.add(player_id)
        cell_x = player["cell_x"]
        cell_y = player["cell_y"]
        username = player["username"]

        if player_id not in cats_by_player_id:
            cats_by_player_id[player_id] = Cat(username, cell_x, cell_y)
        else:
            cat = cats_by_player_id[player_id]
            cat.username = username
            cat.move_to_cell(cell_x, cell_y)

    for player_id in list(cats_by_player_id):
        if player_id not in active_player_ids:
            del cats_by_player_id[player_id]


def update(delta_time):
    """Poll server and update all cats each frame."""
    global last_poll_time
    current_time = time.time()
    if current_time - last_poll_time > 0.2:
        last_poll_time = current_time
        fetch_game_state()

    for cat in cats_by_player_id.values():
        cat.update(delta_time)


def draw():
    """Draw background, coin and all cats."""
    cell_size = config.CELL
    half_cell = cell_size // 2

    for grid_x in range(0, WIDTH, cell_size):
        for grid_y in range(0, HEIGHT, cell_size):
            background_tile = Actor("background", pos=(grid_x + half_cell, grid_y + half_cell))
            background_tile.draw()

    coin_pixel_x = coin_cell[0] * cell_size + half_cell
    coin_pixel_y = coin_cell[1] * cell_size + half_cell
    Actor("coin", pos=(coin_pixel_x, coin_pixel_y)).draw()

    for cat in cats_by_player_id.values():
        cat.draw(screen, Actor)
