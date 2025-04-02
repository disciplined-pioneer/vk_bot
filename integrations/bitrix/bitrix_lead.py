import time
import fast_bitrix24
from settings import settings

# Получает все контакты
async def get_all_contacts():

    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)
    try:
        contacts = await bit.get_all('crm.contact.list', {
            'select': ['ID', 'NAME', 'LAST_NAME', 'UF_CRM_1742556149']
        })
        sorted_contacts = sorted(contacts, key=lambda x: x['ID'], reverse=True)
        return sorted_contacts
    
    except Exception as e:
        print(f"Ошибка при получении контактов: {e}")
        return []


# Создаёт контакт в Bitrix24 или возвращает ID существующего контакта
async def create_contact(link_user: str):

    # Проверяем, существует ли контакт с таким link_user
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)
    all_contacts = await get_all_contacts()

    for contact in all_contacts:
        if contact['UF_CRM_1742556149'] == link_user:
            print(f"Контакт с link_user={link_user} уже существует. ID: {contact['ID']}")
            return contact['ID']

    # Если контакт не найден, создаём новый
    contact_data = {
        'fields': {
            "UF_CRM_1742556149": link_user
        }
    }

    # Создаём контакт
    try:
        contact_id = await bit.call('crm.contact.add', contact_data)
        if isinstance(contact_id, dict) and 'result' in contact_id:
            print(f"Создан контакт с ID: {contact_id['result']}")
            return contact_id['result']
        
        elif isinstance(contact_id, int):
            print(f"Создан контакт с ID: {contact_id}")
            return contact_id
        
        else:
            print(f"Неожиданный формат ответа при создании контакта: {contact_id}")
            return None
        
    except Exception as e:
        print(f"Ошибка при создании контакта: {e}")
        return None


# Создаёт сделку и привязывает к контакту
async def create_deal(contact_id: int, link_post: str, article: str, count: str, params: str):
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL)

    deal_data = {
        'fields': {
            "TITLE": "ВК БОТ ТЕСТ 2", 
            "CONTACT_ID": contact_id,  # Привязка к контакту
            "UF_CRM_1742556368": int(time.time()),
            "UF_CRM_1742556254": link_post,
            "UF_CRM_1742556276": int(article),
            "UF_CRM_1742556311": int(count),
            "UF_CRM_1742556333": params,
            "UF_CRM_1726722554939": "ВК БОТ",
            "STAGE_ID": "NEW", 
        }
    }

    # Создаём сделку
    try:
        deal_id = await bit.call('crm.deal.add', deal_data)
        if isinstance(deal_id, dict) and 'result' in deal_id:
            print(f"Создана сделка с ID: {deal_id['result']}")

        elif isinstance(deal_id, int):
            print(f"Создана сделка с ID: {deal_id}")

        else:
            print(f"Неожиданный формат ответа при создании сделки: {deal_id}")

    except Exception as e:
        print(f"Ошибка при создании сделки: {e}")


# Обрабатывает запрос пользователя: создаёт контакт (если нет), создаёт и привязывает к нему сделку
async def process_user_request(link_user: str, link_post: str, article: str, count: str, params: str):

    contact_id = await create_contact(link_user)

    if contact_id:
        await create_deal(contact_id, link_post, article, count, params)
    else:
        print("Не удалось создать контакт, сделка не будет создана")

