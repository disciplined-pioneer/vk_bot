import re
import httpx
import aiohttp
import requests
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            return await response.json()


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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        return response.json()


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

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if 'response' in data:
        return data['response'][0]['text']
    else:
        print("Ошибка при получении данных:", data)
        return ""


# Извлекает сообщение бота и значение UF_CRM_1742556333 из текста
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
        print(f"\n\nОшибка при запросе к GPT: {e}\n\n")
        return ''