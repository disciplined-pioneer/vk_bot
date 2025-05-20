import time
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
        
        """Возвращает историю диалога (список сообщений) по заданному `parent_id` и `user_id`."""

        messages = await MessagePost.find(
            {
                "$or": [
                    {"parent_id": parent_id},
                    {"comment_id": parent_id}
                ],
                "$and": [
                    {"user_id": user_id}
                ]
            }
        ).sort("timestamp").to_list()

        history = []
        for msg in messages:
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })

        return history


    @classmethod
    async def delete_related_messages(
        cls,
        target_id: int,
        post_id: int,
        group_id: int
    ) -> int:
        """
        Удаляет все сообщения, где comment_id или parent_id равны target_id,
        и совпадают post_id, group_id
        
        Возвращает количество удалённых записей.
        """
        # Найдём подходящие сообщения
        messages_to_delete = await MessagePost.find({
            "$and": [
                {
                    "$or": [
                        {"comment_id": target_id},
                        {"parent_id": target_id}
                    ]
                },
                {"post_id": post_id},
                {"group_id": group_id}
            ]
        }).to_list()

        # Удалим их
        for msg in messages_to_delete:
            await msg.delete()

        return len(messages_to_delete)
    

    @classmethod
    async def get_post_user_map_from_parents(cls) -> Dict[int, List[int]]:
        """
        Ищет сообщения с заданным контентом, извлекает их parent_id.
        По каждому parent_id ищет сообщение, у которого comment_id == parent_id.
        Возвращает словарь вида {post_id: [comment_id, user_id]}.
        """
        trigger_content = "‼️Важно‼️Чтобы мы смогли закрепить за вами товар, напишите нам в сообщения группы👉 http://vk.cc/9WVU0T слово «подтверждаю»"
        
        # Шаг 1: находим все сообщения с нужным content
        trigger_messages = await MessagePost.find({"content": trigger_content}).to_list()

        # Шаг 2: извлекаем уникальные parent_id
        parent_ids = {msg.parent_id for msg in trigger_messages if msg.parent_id is not None}
        if not parent_ids:
            return {}

        # Шаг 3: находим сообщения, у которых comment_id совпадает с parent_id
        matching_messages = await MessagePost.find({
            "comment_id": {"$in": list(parent_ids)}
        }).to_list()

        # Шаг 4: собираем результат в виде {post_id: [comment_id, user_id]}
        result = {}
        for msg in matching_messages:
            if msg.post_id is not None and msg.user_id is not None and msg.comment_id is not None:
                result[msg.post_id] = [msg.comment_id, msg.user_id]

        return result


    @classmethod
    async def auto_cleanup_old_messages(cls) -> int:
        """
        Ищет все сообщения, дата которых >= 2 дня назад,
        и у которых есть comment_id или parent_id.
        Удаляет их с помощью delete_related_messages().
        Возвращает общее количество удалённых сообщений.
        """
        now = int(time.time())
        cutoff = now - 600#2 * 24 * 60 * 60  # 2 дня в секундах

        # Шаг 1: Найти все устаревшие сообщения
        old_messages = await MessagePost.find({
            "date": {"$lte": cutoff},
            "$or": [
                {"comment_id": {"$ne": None}},
                {"parent_id": {"$ne": None}}
            ]
        }).to_list()

        deleted_total = 0

        # Шаг 2: Удаляем каждое сообщение через delete_related_messages
        for msg in old_messages:
            target_id = msg.comment_id if msg.comment_id is not None else msg.parent_id
            if target_id is None or msg.post_id is None or msg.group_id is None:
                continue  # пропускаем некорректные записи

            deleted = await cls.delete_related_messages(target_id, msg.post_id, msg.group_id)
            deleted_total += deleted

        return deleted_total


# Класс для сохранения лидов
class DealBitrix(ModelAdmin):

    date: Optional[int] = None
    link_post: Optional[str] = None
    article: Optional[int] = None
    link_user: Optional[str] = None
    lead_count: Optional[str] = None
    params: Optional[str] = None

    class Settings:
        name = "DealBitrix"


# Класс для сохранения истории личных сообщений
class MessagePrivate(ModelAdmin):

    user_id: Optional[int] = None
    group_id: Optional[int] = None
    peer_id: Optional[int] = None
    id_message: Optional[int] = None
    message_type: Optional[str] = None
    content: Optional[str] = None
    date: Optional[int] = None
    
    class Settings:
        name = 'MessagesPrivate'


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