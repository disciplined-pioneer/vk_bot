import re

from quart import request
from settings import settings
from utils.vk_handler import *
from db.beanie.models.models import MessagePost, MessagePrivate

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

        comment_text = re.sub(r'\[.*?\]\s*,?\s*', '', data["object"]["text"])
        comment_id = data["object"]["id"]
        
        # Определяем тип сообщения
        message_type = 'assistant' if user_id == settings.vk_bot.GROUP_ID else 'user'

        # Асинхронное добавление истории
        await MessagePost.create(
            post_id=post_id,
            group_id=group_id,
            user_id=user_id,
            parent_id=parent_id,
            comment_id=comment_id,
            message_type=message_type,
            content=comment_text,
            date=date
        )

        # Если комментарий от бота, возвращаем "ok"
        if message_type == 'assistant':
            return "ok"

        # Ответ Gpt на сообщение пользователя
        try:
            chat = GPTChat(
                api_key=settings.gpt.API_KEY,
                base_url=settings.gpt.BASE_URL,
                source="post"  
            )

            # Получение ответа и вывод его на экран
            text_post = get_post_text(post_id)
            gpt_resp_text = await chat.chat(
                user_input=comment_text, 
                id_value=parent_id,
                text_post=text_post,
                prompt_path=r"data/openai/prompt.txt"
            )
            send_comment_reply(post_id, comment_id, gpt_resp_text)

        except Exception as e:
            print(f'\nПроизошла ошибка!!!\nОшибка: {e}\n')

    # Обрабатываем ЛС пользователя
    elif data["type"] == "message_new":
        from_id = data["object"]["message"]["from_id"]
        group_id = data["group_id"]
        id_message = data["object"]["message"]["id"]
        peer_id = data["object"]["message"]["peer_id"]
        
        message_type = 'user'
        content = data["object"]["message"]["text"]
        date = data["object"]["message"]["date"]

        # Текст поста, который переслали, если есть
        try:
            text_post = data["object"]["message"]["attachments"][0]["wall"]["text"]
        except:
            text_post = ''

        # Асинхронное добавление истории
        await MessagePrivate.create(
            from_id=from_id,
            group_id=group_id,
            peer_id=peer_id,
            id_message=id_message,
            message_type=message_type,
            content=content,
            date=date,
        )
        
        # Ответ Gpt на сообщение пользователя
        try:
            chat = GPTChat(
                api_key=settings.gpt.API_KEY,
                base_url=settings.gpt.BASE_URL,
                source="private"  
            )

            # Получение ответа и вывод его на экран
            gpt_resp_text = await chat.chat(
                user_input=content,
                text_post=text_post,
                id_value=from_id,  
                prompt_path=r"data/openai/prompt.txt"
            )
            send_private_message(user_id=from_id, text=gpt_resp_text)

        except Exception as e:
            print(f'\nПроизошла ошибка!!!\nОшибка: {e}\n')


    # Обрабатываем ответ бота на ЛС
    elif data["type"] == "message_reply":
        
        from_id =  data["object"]["from_id"]
        group_id = data["group_id"]
        peer_id = data["object"]["peer_id"]
        id_message = data["object"]["id"]
        
        message_type = 'assistant'
        content = data["object"]["text"]
        date = data["object"]["date"]
        
        
        # Асинхронное добавление истории
        await MessagePrivate.create(
            from_id=from_id,
            group_id=group_id,
            peer_id=peer_id,
            id_message=id_message,
            message_type=message_type,
            content=content,
            date=date,
        )
        
        return "ok"

    else:
        pass

    return "ok"

