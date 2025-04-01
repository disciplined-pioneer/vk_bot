import asyncio
import fast_bitrix24
from settings import settings
from utils.bitrix_lead import *

async def create_lead(timestamp: float, link_post: str, article: str, count: int, params: str, link_user: str):
    """Создаёт лид в Bitrix24."""
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)
    date = convert_timestamp_to_date(timestamp)

    tasks = {
        'fields': {
            "TITLE": "ЭТО ТЕСТ ОТ БОТА",
            "UF_CRM_1742556368": date,
            "UF_CRM_1742556254": link_post,
            "UF_CRM_1742556276": article,
            "UF_CRM_1742556311": str(count),  # Приводим к строке, если поле текстовое
            "UF_CRM_1742556333": params,
            "UF_CRM_1742556149": link_user,
            "UF_CRM_1726722554939": "ВК БОТ",
            "STAGE_ID": "NEW",
        }
    }

    try:
        lead_id = await bit.call('crm.lead.add', tasks)  # Ожидание результата
        print(f"Создан лид с ID: {lead_id}")

        lead_data = await bit.call('crm.lead.get', {'id': lead_id})  # Ожидание данных
        print("Данные лида:", lead_data)
    
    except Exception as e:
        print(f"Ошибка при создании лида: {e}")
