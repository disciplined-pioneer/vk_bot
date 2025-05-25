import asyncio
from integrations.bitrix.bitrix_deal import *


async def main():
    result = await get_all_contacts()
    for contact in result:
        print(contact)

    contacts_to_delete = ['196']
    for contact_id in contacts_to_delete:
        await delete_contact(contact_id)

if __name__ == '__main__':
    asyncio.run(main())
