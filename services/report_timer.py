import asyncio
import logging

from utils.vk_handler import send_comment_reply
from integrations.bitrix.bitrix_deal import checking_contact
from db.beanie.models.models import MessageHistoryPost


# Старт задачи
async def run_every_ten_minutes():
    
    await asyncio.sleep(10)
    #print("🔁 Запущено ожидание 1 дня")
    #await asyncio.sleep(24*60*60)
    print("🚀 Активируем задачу.")
    await cancel_expired_exchanges()
    
    print("🔁 Запущено ожидание 1 дня")
    await asyncio.sleep(24*60*60)


# Проверка на "Хочу"
async def cancel_expired_exchanges():

    # Если контакта нет, то пользователь не написал после "Хочу"
    result = await MessageHistoryPost.get_post_user_map_from_parents()
    for post_id, (comment_id, user_id) in result.items():
        link_user = f'https://vk.com/id{user_id}'
        if not await checking_contact(link_user):
            await send_comment_reply(post_id=post_id, comment_id=comment_id, text='Вы начали оформление заказа, но пока не подтвердили его. Пожалуйста, напишите «Хочу» в личные сообщения, чтобы мы могли завершить оформление и сохранить товар за вами.')

    # Удаляем сообщения >= 2-ух дней
    deleted_count = await MessageHistoryPost.auto_cleanup_old_messages()
    print(f"Удалено {deleted_count} устаревших сообщений.")



# Главный цикл репортера, запускается раз в сутки
async def reporter_loop():
    while True:
        try:
            await run_every_ten_minutes()

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")