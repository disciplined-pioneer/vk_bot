import re
import aiohttp
import httpx
import asyncio
from settings import settings
from integrations.OpenAI.gpt_chat import GPTChat

# Функция для ответа на комментарий
async def send_comment_reply(post_id: int, comment_id: int, text: str) -> dict:
    url = "https://api.vk.com/method/wall.createComment"
    params = {
        "owner_id": settings.vk_bot.GROUP_ID,
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": text,
        "access_token": settings.vk_bot.ACCESS_TOKEN,
        "v": "5.199"
    }

    timeout = aiohttp.ClientTimeout(total=60)  # Устанавливаем тайм-аут на 60 секунд

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(url, params=params, ssl=False) as response:
                response.raise_for_status()  # Проверка на ошибки HTTP
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при отправке комментария: {e}")
            return {}
        except asyncio.TimeoutError:
            print("Тайм-аут при отправке комментария")
            return {}


# Функция для ответа на личное сообщение
async def send_private_message(user_id: int, text: str) -> dict:
    url = "https://api.vk.com/method/messages.send"
    params = {
        "peer_id": user_id,
        "message": text,
        "access_token": settings.vk_bot.ACCESS_TOKEN,
        "v": "5.199",
        "random_id": 0
    }

    timeout = 60  # Устанавливаем тайм-аут на 60 секунд

    # Используем httpx с параметром ssl=False для игнорирования проверки SSL-сертификатов
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.post(url, params=params)
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response.json()
        except httpx.RequestError as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return {}
        except httpx.TimeoutException:
            print("Тайм-аут при отправке сообщения")
            return {}


# Функция для получения текста поста
async def get_post_text(post_id: int) -> str:
    access_token = settings.vk_bot.APP_TOKEN
    owner_id = settings.vk_bot.GROUP_ID
    posts = f'{owner_id}_{post_id}'

    url = f'https://api.vk.com/method/wall.getById'
    params = {
        "posts": posts,
        "access_token": access_token,
        "v": "5.131"
    }

    timeout = 60  # Устанавливаем тайм-аут на 60 секунд

    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Проверка на ошибки HTTP
            data = response.json()
            if 'response' in data:
                return data['response'][0]['text']
            else:
                print("Ошибка при получении данных:", data)
                return ""
        except httpx.RequestError as e:
            print(f"Ошибка при получении текста поста: {e}")
            return ""
        except httpx.TimeoutException:
            print("Тайм-аут при получении текста поста")
            return ""


# Извлекает сообщение бота и значение UF_CRM из текста
def parse_vk_bot_response(text: str):

    # Отделяем сообщение от блока с JSON-полями
    split_index = text.find('```')
    message = text[:split_index].strip() if split_index != -1 else text.strip()

    # Проверяем, есть ли текст после блока с кодом (возможное пустое значение)
    json_block = text[split_index + 3:].strip() if split_index != -1 else ""

    # Парсим значения из JSON-блока
    order_info_match = re.search(r'"UF_CRM_1742556333":\s*"(.+?)"', json_block)
    article_match = re.search(r'"UF_CRM_1742556276":\s*"(.+?)"', json_block)
    count_match = re.search(r'"UF_CRM_1742556311":\s*"(.+?)"', json_block)

    order_info = order_info_match.group(1) if order_info_match else None
    article = article_match.group(1) if article_match else None
    count = count_match.group(1) if count_match else None

    return message, article, count, order_info


# Обрабатывает запрос к GPT и возвращает ответ.
async def process_gpt_response(user_id: int, id_value: int,
                               user_input: str, text_post: str,
                               source: str) -> str:
    try:
        chat = GPTChat(
            api_key=settings.gpt.API_KEY,
            base_url=settings.gpt.BASE_URL,
            source=source  
        )
        result = await chat.chat(
            user_input=user_input,
            user_id=user_id,
            id_value=id_value,
            text_post=text_post,
            prompt_path=r"data/openai/prompt.txt"
        )
        return result
    except Exception as e:
        print(f"Ошибка при запросе к GPT: {e}")
        return ''


# Функция для выполнения запроса с повторными попытками в случае ошибок
async def send_request_with_retries(user_id: int, text: str, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            result = await send_private_message(user_id, text)
            if result:  # Если результат успешен, возвращаем его
                return result
            else:
                print(f"Попытка {attempt + 1} не удалась")
        except (aiohttp.ClientError, httpx.RequestError) as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")

        # Экспоненциальная задержка между попытками
        await asyncio.sleep(2 ** attempt)

    print("Все попытки не удались")
    return {}
