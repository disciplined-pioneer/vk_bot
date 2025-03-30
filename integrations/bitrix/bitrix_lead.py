import fast_bitrix24
from settings import settings
from utils.bitrix_lead import *

# Функция для создания лида в Bitrix24
def create_lead(title: str, timestamp: float, link_post: str, article: str, count: int, params: str, comment: str) -> None:
    
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL) 
    date = convert_timestamp_to_date(timestamp)

    # Настройки задачи
    tasks = {
        'fields': {
            "TITLE": title,
            "UF_CRM_1742556368": date, 
            "UF_CRM_1742556254": link_post, 
            "UF_CRM_1742556276": article,  
            "UF_CRM_1742556311": count,  
            "UF_CRM_1742556333": params,  
            "UF_CRM_1726722554939": comment, 
            "STAGE_ID": "NEW",  
        }
    }

    # Создание лида
    lead_id = bit.call('crm.lead.add', tasks)
    print(f"Создан лид с ID: {lead_id}")

    # Получение данных лида
    lead_data = bit.call('crm.lead.get', {'id': lead_id})
    print("Данные лида:", lead_data)
