import re
import asyncio
from quart import request
from settings import settings

from utils.vk_handler import *
from services.cache import handle_comment
from integrations.bitrix.bitrix_deal import *
from db.beanie.models.models import MessagePost, MessageHistoryPost, TempDealLogic, TempDealBitrix


vk_lock = asyncio.Lock()


async def vk_callback():
    
    async with vk_lock:
        
        data = await request.json

        if "secret" in data and data["secret"] != settings.vk_bot.SECRET:
            return "Invalid secret", 403

        # Запрос для проверки
        if data["type"] == "confirmation":
            return settings.vk_bot.CONFIRMATION

        # Комментарий под постом
        if data["type"] == "wall_reply_new":

            # Данные
            user_id = data["object"]["from_id"]
            group_id = data["group_id"]
            post_id = data["object"]["post_id"]
            date = data["object"]["date"]
            parent_id = data["object"].get("parents_stack")
            parent_id = parent_id[0] if isinstance(parent_id, list) and parent_id else None
            comment_text = re.sub(r'\[.*?\]\s*,?\s*', '', data["object"]["text"])
            comment_id = data["object"]["id"]
            message_type = 'assistant' if user_id == settings.vk_bot.GROUP_ID else 'user'

            # В кэше или нет
            if await handle_comment(f"comment_{comment_id}"):
                return "ok"

            # Добавляем в БД сообщение
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
            print(f"\nТекст GPT: {gpt_resp_text}\n")

            # Обработка ответа gpt
            message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)
            if order_info is not None: # Если финал

                # Если контакта нет
                link_user = f'https://vk.com/id{user_id}'
                link_post = f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}"

                result = await checking_contact(link_user)
                if not result:
                    text = '‼️Важно‼️Чтобы мы смогли закрепить за вами товар, напишите нам в сообщения группы👉 http://vk.cc/9WVU0T слово «подтверждаю»'
                    await send_comment_reply(post_id, comment_id, text)

                    # Сохраняем временную сделку
                    await TempDealBitrix.create(
                        date=int(datetime.now(timezone.utc).timestamp() * 1000),
                        link_post=link_post,
                        article=article,
                        link_user=link_user,
                        lead_count=count,
                        params=order_info
                    )
                
                # Удаляем все комментарии
                deleted_count = await MessageHistoryPost.delete_related_messages(
                    target_id=parent_id,
                    post_id=post_id,
                    group_id=group_id
                )
                print(f"Удалено сообщений: {deleted_count}")

                if not result:
                    return "ok"
                
                # Если контакт есть
                async with aiohttp.ClientSession() as session: 
                    await process_user_request(
                        link_user=link_user,
                        link_post=link_post,
                        count=str(count),
                        article=str(article),
                        params=order_info,
                        comment=comment_text,
                        session=session
                    )

            else:
                await send_comment_reply(post_id, comment_id, message_gpt)
            return "ok"


        # Обработка ЛС
        elif data["type"] == "message_new":

            # Проверка на наличие в контактах + запись, если нет
            user_id = data["object"]["message"]["from_id"]
            comment_id = data["object"]["message"]["id"]
            message_user = data["object"]["message"]["text"]
            link_user = f'https://vk.com/id{user_id}'

            if await handle_comment(f"comment_{comment_id}"):
                return "ok"

            async with aiohttp.ClientSession() as session: 
                await create_contact(link_user,
                                session=session)

            # Переносим временные сделки в постоянные
            if message_user.lower() == 'подтверждаю':
                all_deals = await TempDealBitrix.filter(link_user=link_user)
                async with aiohttp.ClientSession() as session: 
                    for deal in all_deals:
                        await process_user_request(
                            link_user=deal.link_user,
                            link_post=deal.link_post,
                            count=str(deal.lead_count),
                            article=str(deal.article),
                            params=deal.params,
                            comment='',
                            session=session
                        )
                        await asyncio.sleep(1)

            # Удаляем все временные сделки
            await TempDealLogic.delete_by_link_user(link_user)

            return "ok"


        """# ЛС ответ бота
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

            return 'ok'"""

        return "ok"
