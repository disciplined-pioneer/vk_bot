from quart import Quart, request
import requests
import asyncio
from pyngrok import ngrok
from db.beanie.models.models import Message
from core.mongo import init_mongo
from settings import settings


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
    if "secret" in data and data["secret"] != settings.vk_bot.SECRET_KEY:
        return "Invalid secret", 403

    # Подтверждение сервера ВК
    if data["type"] == "confirmation":
        return settings.vk_bot.CONFIRMATION_TOKEN

    # Обрабатываем новый комментарий
    if data["type"] == "wall_reply_new":

        user_id = data["object"]["from_id"]
        group_id = data["group_id"]
        post_id = data["object"]["post_id"]
        parent_id = data["object"].get("parents_stack")
        parent_id = parent_id[0] if isinstance(parent_id, list) and parent_id else None

        comment_text = data["object"]["text"].split(', ')[-1]
        comment_id = data["object"]["id"]

        # Проверка: если комментарий от бота, не отвечать на него
        if user_id == settings.vk_bot.GROUP_ID:
            # Асинхронное добавление истории
            await Message.create(
                post_id=post_id,
                group_id=group_id,
                user_id=user_id,
                parent_id=parent_id ,
                comment_id=comment_id,
                message_type='ai',
                message=comment_text,
                timestamp=465
            )
            return "ok"
        
        # Асинхронное добавление истории
        await Message.create(
            post_id=post_id,
            group_id=group_id,
            user_id=user_id,
            parent_id=parent_id,
            comment_id=comment_id,
            message_type='human',
            message=comment_text,
            timestamp=465
        )

        # Отправляем ответ на комментарий
        reply_text = f"Спасибо за комментарий! Мы свяжемся с вами."
        send_comment_reply(post_id, comment_id, reply_text)

    return "ok"

# Отправляем сообщение пользователю
def send_comment_reply(post_id, comment_id, text):
    """Функция для ответа на комментарий"""
    url = "https://api.vk.com/method/wall.createComment"
    params = {
        "owner_id": settings.vk_bot.GROUP_ID, 
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": text,
        "access_token": settings.vk_bot.ACCESS_TOKEN,
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
