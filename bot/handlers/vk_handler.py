import re
import asyncio
import aiohttp
from datetime import datetime, timezone
from quart import request
from settings import settings

from utils.vk_handler import *
from services.cache import handle_comment
from integrations.bitrix.bitrix_deal import *
from db.beanie.models.models import (
    MessagePost,
    MessageHistoryPost,
    TempDealLogic,
    TempDealBitrix,
)

vk_lock = asyncio.Lock()


async def vk_callback():
    async with vk_lock:
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
                date=date,
            )

            if message_type == 'assistant':
                return "ok"

            text_post = await get_post_text(post_id)
            comment_text_full = (
                f"\nТекст поста: {text_post}. Определи все цвета, что тут есть и если он один, "
                f"то сразу записывай! \nТЕКСТ ПОЛЬЗОВАТЕЛЯ: {comment_text}"
            )

            gpt_resp_text = await process_gpt_response(
                source='private',
                user_id=user_id,
                user_input=comment_text_full,
                id_value=user_id,
                text_post=text_post,
            )

            print(comment_text)
            print(f"\nТекст GPT: {gpt_resp_text}\n")

            message_gpt, article, count, order_info = parse_vk_bot_response(gpt_resp_text)

            if order_info is not None:  # Финальная стадия заказа
                link_user = f'https://vk.com/id{user_id}'
                link_post = f"https://vk.com/wall{settings.vk_bot.GROUP_ID}_{post_id}"

                async with aiohttp.ClientSession() as session:
                    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=session)
                    result = await checking_contact(link_user, bit)

                    if not result:
                        text = (
                            '‼️Важно‼️Чтобы мы смогли закрепить за вами товар, '
                            'напишите нам в сообщения группы👉 http://vk.cc/9WVU0T слово «подтверждаю»'
                        )
                        await send_comment_reply(post_id, comment_id, text)

                        await TempDealBitrix.create(
                            date=int(datetime.now(timezone.utc).timestamp() * 1000),
                            link_post=link_post,
                            article=article,
                            link_user=link_user,
                            lead_count=count,
                            params=order_info,
                        )

                    deleted_count = await MessageHistoryPost.delete_related_messages(
                        target_id=parent_id,
                        post_id=post_id,
                        group_id=group_id,
                    )
                    print(f"Удалено сообщений: {deleted_count}")

                    if not result:
                        return "ok"

                    contact_id = await checking_contact(link_user, bit)
                    await process_user_request(
                        link_user=link_user,
                        link_post=link_post,
                        count=str(count),
                        article=str(article),
                        params=order_info,
                        comment=comment_text,
                        client=session,
                        contact_id=contact_id
                    )

            else:
                await send_comment_reply(post_id, comment_id, message_gpt)

            return "ok"

        elif data["type"] == "message_new":
            user_id = data["object"]["message"]["from_id"]
            comment_id = data["object"]["message"]["id"]
            message_user = data["object"]["message"]["text"]
            link_user = f'https://vk.com/id{user_id}'

            if await handle_comment(f"comment_{comment_id}"):
                return "ok"
                
            if message_user.lower() == 'подтверждаю':
                await asyncio.sleep(5)
                
                async with aiohttp.ClientSession() as session:

                    print(f"[DEBUG] Session just created. Closed? {session.closed}")
                    bitr = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=session)

                    contact_id = await update_contact_vk_link_by_name(link=link_user, bit=bitr, client=session)
                    print(f"[DEBUG] After update_contact_vk_link_by_name. Session closed? {session.closed}")

                    all_deals = await TempDealBitrix.filter(link_user=link_user)
                    print(f"[DEBUG] After TempDealBitrix.filter. Session closed? {session.closed}")
                    if all_deals:
                        deal = all_deals[0]
                        if contact_id:
                            await create_deal(contact_id, deal.link_post, str(deal.article), str(deal.lead_count), deal.params, link_user, '', bitr)
                            print(f"[DEBUG] After create_deal. Session closed? {session.closed}")

                print(f"[DEBUG] Session context exited. Session closed? {session.closed}")
                
                """a = await TempDealLogic.delete_by_link_user(link_user)
                print(a)"""


            return "ok"

        return "ok"
