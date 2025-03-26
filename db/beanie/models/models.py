from typing import Optional
from beanie import Document


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


class Message(ModelAdmin):

    user_id: Optional[int] = None
    group_id: Optional[int] = None
    post_id: Optional[int] = None
    parent_comment_id: Optional[int] = None
    
    comment_id: Optional[int] = None
    message_type: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[int] = None

    class Settings:
        name = "Messages"
