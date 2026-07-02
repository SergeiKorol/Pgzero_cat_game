from flask import Flask, jsonify, render_template, request

import database
import game_logic

app = Flask(__name__)

MOVE_ERRORS = {
    "invalid_direction": 400,
    "not_found": 404,
    "still_moving": 409,
    "out_of_bounds": 400,
    "cell_occupied": 409,
}


@app.route("/api/players/join", methods=["POST"])
def api_join():
    """Регистрация игрока."""
    data = request.get_json(silent=True) or {}
    telegram_id = data.get("telegram_id")
    username = data.get("username")
    if telegram_id is None or not username:
        return (
            jsonify(
                {
                    "error": "invalid_request",
                    "message": "Нужны telegram_id и username",
                }
            ),
            400,
        )

    conn = database.get_connection()
    try:
        result = game_logic.join_player(int(telegram_id), str(username), conn)
    except RuntimeError:
        return (
            jsonify(
                {"error": "no_free_cells", "message": "Игровое поле заполнено"}
            ),
            400,
        )
    finally:
        conn.close()
    return jsonify(result)


@app.route("/api/players/<int:telegram_id>/move", methods=["POST"])
def api_move(telegram_id: int):
    """Перемещение кота."""
    data = request.get_json(silent=True) or {}
    direction = data.get("direction")
    conn = database.get_connection()
    try:
        result = game_logic.move_player(telegram_id, direction, conn)
    except ValueError as exc:
        error_code = str(exc)
        status = MOVE_ERRORS.get(error_code, 400)
        return jsonify({"error": error_code}), status
    finally:
        conn.close()
    return jsonify(result)


@app.route("/api/game/state", methods=["GET"])
def api_game_state():
    """Состояние поля для игрового окна."""
    conn = database.get_connection()
    try:
        return jsonify(game_logic.get_game_state(conn))
    finally:
        conn.close()


@app.route("/leaderboard")
def page_leaderboard():
    """HTML-таблица лидеров."""
    conn = database.get_connection()
    try:
        rows = game_logic.leaderboard(conn)
    finally:
        conn.close()
    return render_template("leaderboard.html", rows=rows)


@app.route("/ai-skills")
def page_ai():
    """Страница о навыках работы с ИИ."""
    return render_template("ai_skills.html")


if __name__ == "__main__":
    database.init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
