from quart import request
from db.beanie.models.models import Message
from settings import settings
from utils.vk_handler import *

async def vk_callback():
    data = await request.json

    # Проверяем секретный ключ
    if "secret" in data and data["secret"] != settings.vk_bot.SECRET:
        return "Invalid secret", 403

    # Подтверждение сервера ВК
    if data["type"] == "confirmation":
        return settings.vk_bot.CONFIRMATION

    # Обрабатываем новый комментарий
    if data["type"] == "wall_reply_new":
        user_id = data["object"]["from_id"]
        group_id = data["group_id"]
        post_id = data["object"]["post_id"]
        parent_id = data["object"].get("parents_stack")
        parent_id = parent_id[0] if isinstance(parent_id, list) and parent_id else None

        comment_text = data["object"]["text"].split(', ')[-1]
        comment_id = data["object"]["id"]
        
        # Определяем тип сообщения
        message_type = 'ai' if user_id == settings.vk_bot.GROUP_ID else 'human'

        # Асинхронное добавление истории
        await Message.create(
            post_id=post_id,
            group_id=group_id,
            user_id=user_id,
            parent_id=parent_id,
            comment_id=comment_id,
            message_type=message_type,
            message=comment_text,
            timestamp=465
        )

        # Если комментарий от бота, сразу возвращаем "ok"
        if message_type == 'ai':
            return "ok"

        text_post = get_post_text(post_id)
        print(f"\nТЕКСТ ПОСТА: {text_post}\n")

        # Отправляем ответ на комментарий
        reply_text = f"Спасибо за комментарий! Мы свяжемся с вами."
        send_comment_reply(post_id, comment_id, reply_text)

    return "ok"

