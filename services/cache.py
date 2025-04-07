import asyncio
from aiocache import SimpleMemoryCache

cache = SimpleMemoryCache()
lock = asyncio.Lock()

MAX_CACHE_SIZE = 70  # макс. 30 комментариев
TTL = 60  # 1 минута

async def handle_comment(comment_id: str) -> bool:
    async with lock:
        key = f"comment_{comment_id}"

        if await cache.get(key) is not None:
            return True

        # Добавляем в кэш новый комментарий
        await cache.set(key, True, ttl=TTL)

        # Получаем список последних комментариев
        recent_comments = await cache.get("recent_comments") or []

        # Обновляем список
        recent_comments.append(comment_id)

        # Ограничиваем размер списка
        if len(recent_comments) > MAX_CACHE_SIZE:
            removed_comment = recent_comments.pop(0)
            await cache.delete(f"comment_{removed_comment}")  # удаляем устаревший ключ

        # Обновляем список в кэше (без TTL, живёт вечно)
        await cache.set("recent_comments", recent_comments)

        return False
