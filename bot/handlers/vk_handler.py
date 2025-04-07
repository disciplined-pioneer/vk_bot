from quart import request
from settings import settings
import re

from services.cache import handle_comment
from utils.vk_handler import *
from integrations.bitrix.bitrix_deal import *
from db.beanie.models.models import MessagePost, MessagePrivate

async def vk_callback():
    data = await request.json

    if "secret" in data and data["secret"] != settings.vk_bot.SECRET:
        return "Invalid secret", 403

    if data["type"] == "confirmation":
        return settings.vk_bot.CONFIRMATION

    if data["type"] == "wall_reply_new":
        user_id = data["object"]["from_id"]
        group_id = data["group_id"]
        post_id = data["object"]["post_id"]
        date = data["object"]["date"]

        parent_id = data["object"].get("parents_stack")
        parent_id = parent_id[0] if isinstance(parent_id, list) and parent_id else None

        comment_text = re.sub(r'\[.*?\]\s*,?\s*', '', data["object"]["text"])
        comment_id = data["object"]["id"]

        message_type = 'assistant' if user_id == settings.vk_bot.GROUP_ID else 'user'

        if await handle_comment(f"comment_{comment_id}"):
            return "ok"

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

        if message_type == 'assistant':
            return "ok"

        text_post = await get_post_text(post_id)
        comment_text_full = f"\nТекст поста: {text_post}. Определи все цвета, что тут есть и если он один, то сразу записывай! \nТЕКСТ ПОЛЬЗОВАТЕЛЯ: {comment_text}"

        gpt_resp_text = await process_gpt_response(
            source='private',
            user_id=user_id,
            user_input=comment_text_full,
            id_value=user_id,
            text_post=text_post
        )

        print(comment_text)
        #print(f"\nТекст GPT: {gpt_resp_text}\n")

        message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)
        if order_info is not None:
            await process_user_request(
                link_user=f"https://vk.com/id{user_id}",
                link_post=f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}",
                count=str(count),
                article=str(article),
                params=order_info
            )

        await send_comment_reply(post_id, comment_id, message_gpt)
        return "ok"

    elif data["type"] == "message_new":
        user_id = data["object"]["message"]["from_id"]
        group_id = data["group_id"]
        id_message = data["object"]["message"]["id"]
        peer_id = data["object"]["message"]["peer_id"]
        content = data["object"]["message"]["text"]
        date = data["object"]["message"]["date"]

        if await handle_comment(f"comment_{id_message}"):
            return "ok"

        try:
            post_inf = data["object"]["message"]["attachments"][0]["wall"]
            post_id = post_inf["id"]
            date = post_inf["date"]
            text_post = post_inf["text"]
        except:
            text_post = ''

        await MessagePrivate.create(
            user_id=user_id,
            group_id=group_id,
            peer_id=peer_id,
            id_message=id_message,
            message_type='user',
            content=content,
            date=date,
        )
        content_full = f"\nТекст поста: {text_post}. Определи все цвета, что тут есть и если он один, то сразу записывай! \nТЕКСТ ПОЛЬЗОВАТЕЛЯ: {comment_text}"

        gpt_resp_text = await process_gpt_response(
            source='private',
            user_id=user_id,
            user_input=content_full,
            id_value=user_id,
            text_post=text_post
        )
       

        message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)
        if order_info is not None:
            await process_user_request(
                link_user=f"https://vk.com/id{user_id}",
                link_post=f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}",
                count=str(count),
                article=str(article),
                params=order_info
            )
        await send_private_message(user_id, message_gpt)
        return "ok"

    elif data["type"] == "message_reply":
        user_id = data["object"]["from_id"]
        group_id = data["group_id"]
        peer_id = data["object"]["peer_id"]
        id_message = data["object"]["id"]
        content = data["object"]["text"]
        date = data["object"]["date"]

        await MessagePrivate.create(
            user_id=user_id,
            group_id=group_id,
            peer_id=peer_id,
            id_message=id_message,
            message_type='assistant',
            content=content,
            date=date,
        )

        return "ok"

    return "ok"
