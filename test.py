import asyncio
from integrations.bitrix.bitrix_deal import *

from core.http_client import close_client


async def main():
    
    result = await get_all_contacts()
    for contact in result:
        print(contact)

    try:
        contacts_to_delete = ['268']
        for contact_id in contacts_to_delete:
            await delete_contact(contact_id)
    except:
        pass
    
    await close_client()

if __name__ == '__main__':
    asyncio.run(main())


"""import requests

webhook_url = 'https://b24-n8nava.bitrix24.ru/rest/60/7ts1m4u7e3egpyrt/'

response = requests.get(webhook_url + 'scope.json')
print("→ Доступные права:")
print(response.json())
"""