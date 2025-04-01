import fast_bitrix24
from settings import settings
from utils.bitrix_lead import *
from db.beanie.models.models import LeadBitrix

# Создаёт лид в Bitrix24
async def create_lead(timestamp: float, link_post: str, article: str, count: str, params: str, link_user: str):
   
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)
    date = convert_timestamp_to_date(timestamp)

    tasks = {
        'fields': {
            "TITLE": "ЭТО ТЕСТ ОТ БОТА",
            "UF_CRM_1742556368": date,
            "UF_CRM_1742556254": link_post,
            "UF_CRM_1742556276": article,
            "UF_CRM_1742556311": count, 
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

        await LeadBitrix.create(date=timestamp,
                         link_post=link_post,
                         article=article,
                         link_user=link_user,
                         lead_counts=count,
                         params=params)
    
    except Exception as e:
        print(f"Ошибка при создании лида: {e}")
