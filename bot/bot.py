import requests
import telebot

BOT_TOKEN = "Сюда пиши свой токен"

bot = telebot.TeleBot(BOT_TOKEN)

URL = "http://127.0.0.1:5000"


def keys():
    k = telebot.types.InlineKeyboardMarkup()
    k.row(telebot.types.InlineKeyboardButton("U", callback_data="move_up"))
    k.row(
        telebot.types.InlineKeyboardButton("L", callback_data="move_left"),
        telebot.types.InlineKeyboardButton("R", callback_data="move_right"),
    )
    k.row(telebot.types.InlineKeyboardButton("D", callback_data="move_down"))
    return k


@bot.message_handler(commands=["join"])
def join(msg):
    u = msg.from_user
    requests.post(f"{URL}/api/players/join", json={
        "telegram_id": u.id,
        "username": u.username or str(u.id),
    })
    bot.send_message(msg.chat.id, "Play", reply_markup=keys())


@bot.callback_query_handler(func=lambda c: c.data.startswith("move_"))
def move(call):
    d = call.data.replace("move_", "")
    requests.post(f"{URL}/api/players/{call.from_user.id}/move", json={"direction": d})
    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    bot.infinity_polling()