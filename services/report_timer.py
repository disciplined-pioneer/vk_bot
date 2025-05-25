import asyncio
import logging

from utils.vk_handler import send_comment_reply
from integrations.bitrix.bitrix_deal import checking_contact
from db.beanie.models.models import MessageHistoryPost, TempDealLogic


# Старт задачи
async def run_every_ten_minutes():
    
    print("🔁 Запущено ожидание 10 минут")
    await asyncio.sleep(600)
    print("🚀 Активируем задачу.")
    await cancel_expired_exchanges()


# Проверка на "Хочу"
async def cancel_expired_exchanges():

    # Если контакта нет, то пользователь не написал после "Хочу"
    result = await MessageHistoryPost.get_post_user_map_from_parents()
    for post_id, (comment_id, user_id) in result.items():
        link_user = f'https://vk.com/id{user_id}'
        if not await checking_contact(link_user):
            await send_comment_reply(post_id=post_id, comment_id=comment_id, text='Вы начали оформление заказа, но пока не подтвердили его. Пожалуйста, напишите «Хочу» в личные сообщения, чтобы мы могли завершить оформление и сохранить товар за вами.')

    # Удаляем сообщения >= 2 дня
    deleted_count = await MessageHistoryPost.auto_cleanup_old_messages()
    await TempDealLogic.delete_old_records()
    print(f"Удалено {deleted_count} устаревших сообщений.")



# Главный цикл репортера, запускается раз в сутки
async def reporter_loop():
    while True:
        try:
            await run_every_ten_minutes()

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")