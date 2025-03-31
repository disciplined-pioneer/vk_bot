from typing import Optional
from beanie import Document
from typing import List, Dict, Optional


# Базовый класс для CRUD-операций
class ModelAdmin(Document):

    class CellTypeExp(Exception):
        pass

    @classmethod
    async def create(cls, **kwargs):
        """
        Создает новый объект и вставляет его в базу данных.
        """
        obj = cls(**kwargs)
        await obj.insert()
        return obj

    async def update(self, **kwargs):
        """
        Обновляет поля объекта новыми значениями.
        """
        _set = {"$set": {}}

        for key, value in kwargs.items():
            if not self.__dict__.get(key):
                raise self.CellTypeExp(f"В модели `{self.__class__.__name__}` отсутствует поле `{key}`")
            elif not isinstance(self.__dict__.get(key), type(value)):
                raise self.CellTypeExp(
                    f"Тип данных поля `{key}` модели `{self.__class__.__name__}` является {type(self.__dict__.get(key))} (не {type(value)})")
            _set["$set"][key] = value

        await super().update(_set)

    async def delete(self):
        """
        Удаляет объект из базы данных.
        """
        await super().delete()

    @classmethod
    async def get(cls, **kwargs):
        """
        Возвращает один объект, соответствующий критериям поиска.
        """
        return await cls.find_one(kwargs)

    @classmethod
    async def check(cls, **kwargs) -> Optional[str]:
        """
        Проверяет наличие объекта, соответствующего критериям поиска, и возвращает его ID.
        """
        obj = await cls.find_one(kwargs)
        return str(obj.id) if obj else None

    @classmethod
    async def filter(cls, **kwargs):
        """
        Возвращает список объектов, соответствующих критериям поиска.
        """
        return await cls.find(kwargs).to_list()

    @classmethod
    async def all(cls):
        """
        Возвращает список всех объектов.
        """
        return await cls.find_all().to_list()


# Класс для сохранения истории сообщений под постами
class MessagePost(ModelAdmin):

    post_id: Optional[int] = None
    group_id: Optional[int] = None
    
    user_id: Optional[int] = None
    parent_id: Optional[int] = None
    
    comment_id: Optional[int] = None
    message_type: Optional[str] = None
    content: Optional[str] = None
    date: Optional[int] = None

    class Settings:
        name = "MessagesPost"


# Этот класс получения истории сообщений
class MessageHistoryPost:

    @classmethod
    async def get_dialog_history(cls, parent_id: int, user_id: int) -> List[Dict[str, str]]:
        # Получаем все сообщения с parent_id или comment_id == parent_id
        messages = await MessagePost.find(
            {"$or": [
                {"parent_id": parent_id},
                {"comment_id": parent_id}
                ],
            "$and": [
                {"user_id": user_id}
            ]
            }
        ).sort("timestamp").to_list()

        # Формируем историю
        history = []
        for msg in messages:
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })

        return history


# Класс для сохранения истории личных сообщений
class MessagePrivate(ModelAdmin):

    from_id: Optional[int] = None
    group_id: Optional[int] = None
    peer_id: Optional[int] = None
    id_message: Optional[int] = None
    message_type: Optional[str] = None
    content: Optional[str] = None
    date: Optional[int] = None
    
    class Settings:
        name = "MessagesPrivate"


# Этот класс получения истории личных сообщений
class MessageHistoryPrivate:

    @classmethod
    async def get_dialog_history(cls, user_id: int) -> List[Dict[str, str]]:
        # Получаем все сообщения, где from_id == user_id или peer_id == user_id
        messages = await MessagePrivate.find(
            {"$or": [
                {"from_id": user_id},
                {"peer_id": user_id}  # Ищем сообщения с peer_id == user_id
            ]}
        ).sort("date").to_list()

        # Формируем историю
        history = []
        for msg in messages:
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })

        return history

