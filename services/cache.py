import asyncio
from aiocache import SimpleMemoryCache

cache = SimpleMemoryCache()

MAX_CACHE_SIZE = 30  # макс. 30 комм.
TTL = 300  # 5 мин - врем хранения


# Проверка существования комментария в кэше
async def handle_comment(comment_id: str) -> bool:

    if await cache.get(f"comment_{comment_id}") is not None:
        return True
    
    # Добавляем comment_id в кэш
    await cache.set(f"comment_{comment_id}", True, ttl=TTL)

    # Список последних комментариев
    recent_comments = await cache.get("recent_comments") or []
    recent_comments.append(comment_id)

    # Ограничиваем список
    if len(recent_comments) > MAX_CACHE_SIZE:
        removed = recent_comments.pop(0)
        await cache.delete(f"comment_{removed}")  # Удаляем старый комментарий

    # Обновляем кэш с новым списком комментариев
    await cache.set("recent_comments", recent_comments, ttl=TTL)

    return False