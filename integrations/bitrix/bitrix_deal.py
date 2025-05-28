import re
import fast_bitrix24
from settings import settings
from datetime import datetime, timezone
from db.beanie.models.models import DealBitrix

from core.http_client import get_client


# Удаление контакта по его id
async def delete_contact(contact_id):

    client = await get_client()
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=client)
    response = await bit.call('crm.contact.delete', {'id': contact_id})
    if response is True:
        print(f"[+] Контакт {contact_id} успешно удалён.")
    else:
        print(f"[!] Не удалось удалить контакт {contact_id}: {response}")


# Получает все контакты
async def get_all_contacts():

    client = await get_client()
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=client)
    try:
        contacts = await bit.get_all('crm.contact.list', {
            'select': ['ID', 'NAME', 'LAST_NAME', 'UF_CRM_1742556149']
        })
        sorted_contacts = sorted(contacts, key=lambda x: int(x['ID']), reverse=True)
        return sorted_contacts
    except Exception as e:
        print(f"Ошибка при получении контактов: {e}")
        return []

    
# Обновление ссылки по фамилии и имени
async def update_contact_vk_link_by_name(link: str):

    client = await get_client()
    contacts = await get_all_contacts()
    first_name, last_name = await get_vk_name(link_user=link)

    target_contact = next(
        (c for c in contacts if c.get("NAME") == first_name and c.get("LAST_NAME") == last_name),
        None
    )

    if not target_contact:
        print(f"[❌] Контакт '{first_name} {last_name}' не найден.")
        return
    
    contact_id = target_contact["ID"]
    print(contact_id, target_contact)
    current_value = target_contact.get("UF_CRM_1742556149")

    if current_value:
        print(f"[⏩] Контакт {first_name} {last_name} уже имеет ссылку: {current_value}")
        return contact_id

    async with client.post(
        f"{settings.bitrix24.URL}/crm.contact.update",
        data={
            "id": contact_id,
            "fields[UF_CRM_1742556149]": link
        }
    ) as resp:
        result = await resp.json()
        if result.get("error"):
            print(f"[❌] Ошибка при обновлении контакта {contact_id}: {result['error_description']}")
            return None
        else:
            print(f"[✅] Контакт {first_name} {last_name} обновлён. Ссылка: {link}")
            return contact_id


# Проверка на наличие контакта
async def checking_contact(link_user: str):
    all_contacts = await get_all_contacts()
    for contact in all_contacts:
        if contact['UF_CRM_1742556149'] == link_user:
            print(f"Контакт с link_user={link_user} уже существует. ID: {contact['ID']}")
            return contact['ID']
    return False


"""# Создаёт контакт в Bitrix24 или возвращает ID
async def create_contact(link_user: str, client: aiohttp.ClientSession):
    contact_id = await checking_contact(link_user, client)
    if contact_id:
        return contact_id

    first_name, last_name = await get_vk_name(link_user, client)
    contact_data = {
        'fields': {
            'NAME': first_name,
            'LAST_NAME': last_name,
            'UF_CRM_1742556149': link_user
        }
    }

    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=client)
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
        return None"""


# Создаёт сделку и привязывает к контакту
async def create_deal(contact_id: int, link_post: str, article: str, count: str, params: str, link_user: str, comment: str):
    
    client = await get_client()
    bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=client)

    date = int(datetime.now(timezone.utc).timestamp() * 1000)
    article = re.sub(r"\D", "", article)
    deal_data = {
        'fields': {
            "TITLE": "ВК БОТ", 
            "CONTACT_ID": contact_id,
            "UF_CRM_1742556368": date,
            "UF_CRM_1742556254": link_post,
            "UF_CRM_1742556276": article,
            "UF_CRM_1742556311": count,
            "UF_CRM_1742556333": params,
            "UF_CRM_1726722554939": comment,
            "STAGE_ID": "NEW"
        }
    }

    try:
        deal_id = await bit.call('crm.deal.add', deal_data)
        
        if isinstance(deal_id, dict) and 'result' in deal_id:
            print(f"Создана сделка с ID: {deal_id['result']}")
        elif isinstance(deal_id, int):
            print(f"Создана сделка с ID: {deal_id}")
        else:
            print(f"Неожиданный формат ответа при создании сделки: {deal_id}")

        await DealBitrix.create(
            date=date,
            link_post=link_post,
            article=article,
            link_user=link_user,
            lead_count=count,
            params=params
        )
    except Exception as e:
        print(f"Ошибка при создании сделки: {e}")


# Обрабатывает запрос пользователя, создаёт и привязывает к нему сделку
async def process_user_request(link_user: str, link_post: str, article: str, count: str, params: str, contact_id, comment: str = ''):
    if contact_id:
        await create_deal(contact_id, link_post, article, count, params, link_user, comment)


# Получение данных пользователя
async def get_vk_name(link_user: str):

    client = await get_client()
    user_id = link_user.split("id")[-1]
    url = "https://api.vk.com/method/users.get"
    params = {
        "access_token": settings.vk_bot.ACCESS_TOKEN,
        "user_ids": user_id,
        "v": "5.131"
    }

    async with client.get(url, params=params, ssl=False) as response:
        data = await response.json()
        first_name = data['response'][0]['first_name']
        last_name = data['response'][0]['last_name']
        return first_name, last_name
