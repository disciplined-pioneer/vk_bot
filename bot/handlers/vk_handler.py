import re

from quart import request
from settings import settings

from services.cache import handle_comment

from utils.vk_handler import *
from integrations.bitrix.bitrix_deal import *
from db.beanie.models.models import MessagePost, MessagePrivate


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

        # Проверка на существование комментария в кэше и его добавление
        if await handle_comment(f"comment_{comment_id}"):
            return "ok"

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
        
        # Запрос в GPT
        text_post = get_post_text(post_id)
        gpt_resp_text = await process_gpt_response(source='post',
                                                   user_id=user_id,
                                                   user_input=comment_text,
                                                   id_value=parent_id,
                                                   text_post=text_post)
            
        # Отправляем Лид, если он есть
        message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)
        if order_info is not None:
            await process_user_request(link_user=f"https://vk.com/id{user_id}",
                                       link_post=f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}",
                                       count=str(count),
                                       article=str(article),
                                       params=order_info)
        send_comment_reply(post_id, comment_id, message_gpt)


    # Обрабатываем ЛС пользователя
    elif data["type"] == "message_new":
        user_id = data["object"]["message"]["from_id"]
        group_id = data["group_id"]
        id_message = data["object"]["message"]["id"]
        peer_id = data["object"]["message"]["peer_id"]
        
        message_type = 'user'
        content = data["object"]["message"]["text"]
        date = data["object"]["message"]["date"]

        # Проверка на существование комментария в кэше и его добавление
        if await handle_comment(f"comment_{id_message}"):
            return "ok"

        # Текст поста, который переслали, если есть
        try:
            post_inf = data["object"]["message"]["attachments"][0]["wall"]
            post_id = post_inf["id"]
            date = post_inf["date"]
            text_post = post_inf["text"]
        except:
            text_post = ''

        # Асинхронное добавление истории
        await MessagePrivate.create(
            user_id=user_id,
            group_id=group_id,
            peer_id=peer_id,
            id_message=id_message,
            message_type=message_type,
            content=content,
            date=date,
        )
    
        # Запрос в GPT
        gpt_resp_text = await process_gpt_response(source='private',
                                                   user_id=user_id,
                                                   user_input=content,
                                                   id_value=user_id,
                                                   text_post=text_post)
            
        # Отправляем Лид, если он есть
        message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)
        if order_info is not None:
            await process_user_request(link_user=f"https://vk.com/id{user_id}",
                                       link_post=f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}",
                                       count=str(count),
                                       article=str(article),
                                       params=order_info)
        send_private_message(user_id, message_gpt)


    # Обрабатываем ответ бота на ЛС
    elif data["type"] == "message_reply":
        
        user_id =  data["object"]["from_id"]
        group_id = data["group_id"]
        peer_id = data["object"]["peer_id"]
        id_message = data["object"]["id"]
        
        message_type = 'assistant'
        content = data["object"]["text"]
        date = data["object"]["date"]
        
        # Асинхронное добавление истории
        await MessagePrivate.create(
            user_id=user_id,
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