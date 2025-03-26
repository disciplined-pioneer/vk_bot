from core.mongo import init_mongo
from db.beanie.models.models import User
import asyncio

async def main():
    # Инициализация MongoDB
    await init_mongo()

    # Создание пользователя
    user = await User.create(tg_id=12555553, full_name="Иван Иванов")
    print(f"Создан пользователь с ID: {user.id}")

    # Удаление пользователя с tg_id = 1234567890
    user_to_delete = await User.find_one(User.tg_id == 1234567890)
    if user_to_delete:
        await user_to_delete.delete()
        print("Пользователь с tg_id 1234567890 удален.")
    else:
        print("Пользователь с tg_id 1234567890 не найден.")

    # Получение всех пользователей
    all_users = await User.find_all().to_list()
    for user in all_users:
        print(f"\n{user}")

if __name__ == "__main__":
    asyncio.run(main())