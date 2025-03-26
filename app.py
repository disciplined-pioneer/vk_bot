from quart import Quart, request
import requests
import asyncio
from pyngrok import ngrok
from db.beanie.models.models import Message
from core.mongo import init_mongo

# Конфигурация
SECRET_KEY = "obama"
ACCESS_TOKEN = "vk1.a.Ky0wxlpHEU97ml2RH8nUXGRw5zBSXMLmRHFCeTbJH4FM6_T4Mrl_k7YtPjq9rYvbAoP5jkMTydVFlWk2aPhgl5Q-aZ7DWMu4hCMIMb7OgAHBdis8Ls2sM0SenAfXKF3FmhcWpQnaSEcpKkvQnX6S4aOG3-PTdj6hBIR4HHTck93zWkRyErb5xGsMzZta9v3yRTdotFiRN9dw1fxgmKRCug"
CONFIRMATION_TOKEN = "5f9af579"
GROUP_ID = -229856852

app = Quart(__name__)

# Инициализация MongoDB
async def init_db():
    await init_mongo()

@app.before_serving
async def before_serving():
    await init_db()

# Пример маршрута Quart
@app.route("/", methods=["POST"])
async def vk_callback():
    data = await request.json

    # Проверяем секретный ключ
    if "secret" in data and data["secret"] != SECRET_KEY:
        return "Invalid secret", 403

    # Подтверждение сервера ВК
    if data["type"] == "confirmation":
        return CONFIRMATION_TOKEN

    # Обрабатываем новый комментарий
    if data["type"] == "wall_reply_new":

        user_id = data["object"]["from_id"]
        group_id = data["group_id"]
        post_id = data["object"]["post_id"]
        parent_comment_id = data["object"].get("reply_to_comment")

        comment_text = data["object"]["text"].split(', ')[-1]
        comment_id = data["object"]["id"]

        # Проверка: если комментарий от бота, не отвечать на него
        if user_id == GROUP_ID:
            return "ok"

        # Асинхронное добавление истории
        await Message.create(
            user_id=user_id,
            group_id=group_id,
            post_id=post_id,
            parent_comment_id=parent_comment_id,

            comment_id=comment_id,
            message_type='men',
            message=comment_text,
            timestamp=465  # Используйте timestamp вместо datetime
        )
        message_from_db = await Message.all()
        print(message_from_db)

        # Отправляем ответ на комментарий
        reply_text = f"Спасибо за комментарий! Мы свяжемся с вами."
        send_comment_reply(post_id, comment_id, reply_text)

    return "ok"

# Отправляем сообщение пользователю
def send_comment_reply(post_id, comment_id, text):
    """Функция для ответа на комментарий"""
    url = "https://api.vk.com/method/wall.createComment"
    params = {
        "owner_id": GROUP_ID, 
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": text,
        "access_token": ACCESS_TOKEN,
        "v": "5.199"
    }
    response = requests.post(url, params=params)
    print(f"\nAPI: {response.json()}")
    return response.json()

if __name__ == "__main__":
    # Запускаем ngrok и выводим URL
    public_url = ngrok.connect(5000).public_url
    print(f"Ngrok URL: {public_url}")

    # Запускаем сервер Quart
    app.run(host="0.0.0.0", port=5000)
