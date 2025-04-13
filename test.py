import asyncio
import fast_bitrix24
from settings import settings

fields = [
    "TITLE",
    "CONTACT_ID",
    "UF_CRM_1742556368",
    "UF_CRM_1742556254",
    "UF_CRM_1742556276",
    "UF_CRM_1742556311",
    "UF_CRM_1742556333",
    "UF_CRM_1726722554939",
    "STAGE_ID"
]


# Получает последние 5 сделок с полным набором полей
async def get_last_5_deals():
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)
    try:
        # Получаем все сделки с полным набором полей
        deals = await bit.get_all('crm.deal.list', {
            'select': fields
        })

        # Сортируем по убыванию ID (последние — с наибольшим ID)
        sorted_deals = sorted(deals, key=lambda x: int(x['ID']), reverse=True)

        # Берём только последние 5 сделок
        last_5_deals = sorted_deals[:5]

        # Выводим каждую сделку
        for i, deal in enumerate(last_5_deals, 1):
            print(f"\nСделка #{i}")
            for key, value in deal.items():
                print(f"{key}: {value}")

        return last_5_deals

    except Exception as e:
        print(f"Ошибка при получении сделок: {e}")
        return []
    


asyncio.run(get_last_5_deals())
