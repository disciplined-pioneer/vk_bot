import time
import fast_bitrix24

# Создаёт лид в Bitrix24
async def create_lead(timestamp: float, link_post: str, article: str, count: str, params: str, link_user: str):
   
    bit = fast_bitrix24.Bitrix('https://b24-n8nava.bitrix24.ru/rest/60/7ts1m4u7e3egpyrt/')
    date = int(time.time())  # Текущая дата в формате timestamp

    tasks = {
        'fields': {
            "TITLE": "ЭТО ТЕСТ ОТ БОТА234",
            "UF_CRM_1742556368": date,
            "UF_CRM_1742556254": link_post,
            "UF_CRM_1742556276": 1,
            "UF_CRM_1742556311": 1, 
            "UF_CRM_1742556333": params,
            "UF_CRM_1742556149": link_user,
            "UF_CRM_1726722554939": "ВК БОТ",
            "STAGE_ID": "NEW",
        }
    }

    try:
        lead_id = await bit.call('crm.deal.add', tasks)  # Ожидание результата
        print(f"Создан лид с ID: {lead_id}")

        lead_data = await bit.call('crm.deal.get', {'id': lead_id})  # Ожидание данных
        print("Данные лида:", lead_data)

    except Exception as e:
        print(f"Ошибка при создании лида: {e}")

import asyncio

asyncio.run(create_lead(1689084000, "https://example.com", "Article", "Count", "Params", "UserLink"))
