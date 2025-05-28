import asyncio
from integrations.bitrix.bitrix_deal import *


async def main():
    
    async with aiohttp.ClientSession() as session:
        bit = fast_bitrix24.Bitrix(settings.bitrix24.URL, client=session)
        result = await get_all_contacts(bit)
        for contact in result:
            print(contact)

    try:
        async with aiohttp.ClientSession() as session:
            contacts_to_delete = ['266']
            for contact_id in contacts_to_delete:
                await delete_contact(contact_id, client=session)
    except:
        pass

if __name__ == '__main__':
    asyncio.run(main())


"""import requests

webhook_url = 'https://b24-n8nava.bitrix24.ru/rest/60/7ts1m4u7e3egpyrt/'

response = requests.get(webhook_url + 'scope.json')
print("→ Доступные права:")
print(response.json())
"""