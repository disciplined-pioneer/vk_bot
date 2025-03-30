import re

from quart import request
from settings import settings
from utils.vk_handler import *
from db.beanie.models.models import Message

from integrations.OpenAI.gpt_chat import GPTChat

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
        date = data["object"]["date"]

        parent_id = data["object"].get("parents_stack")
        parent_id = parent_id[0] if isinstance(parent_id, list) and parent_id else None

        comment_text = re.sub(r'\[.*?\]\s*', '', data["object"]["text"])
        comment_id = data["object"]["id"]
        
        # Определяем тип сообщения
        message_type = 'assistant' if user_id == settings.vk_bot.GROUP_ID else 'user'

        # Асинхронное добавление истории
        await Message.create(
            post_id=post_id,
            group_id=group_id,
            user_id=user_id,
            parent_id=parent_id,
            comment_id=comment_id,
            message_type=message_type,
            content=comment_text,
            timestamp=date
        )

        # Если комментарий от бота, возвращаем "ok"
        if message_type == 'assistant':
            return "ok"

        text_post = get_post_text(post_id)
        print(f"\nТЕКСТ ПОСТА: {text_post}\n")

        # Ответ Gpt на сообщение пользователя
        try:
            chat = GPTChat(
                api_key=settings.gpt.API_KEY,
                base_url=settings.gpt.BASE_URL,
            )

            # Получение ответа и вывод его на экран
            gpt_resp_text = await chat.chat(comment_text, parent_id=parent_id, prompt_path=r"data/openai/prompt.txt")
            print(f"\nGPT: {gpt_resp_text}\n")

            send_comment_reply(post_id, comment_id, gpt_resp_text)

        except Exception as e:
            print(f'\nПроизошла ошибка!!!\nОшибка: {e}\n')

    return "ok"

