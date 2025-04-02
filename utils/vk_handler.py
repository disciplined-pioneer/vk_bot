import re
import requests
from settings import settings
from integrations.OpenAI.gpt_chat import GPTChat

# Функция для ответа на комментарий
def send_comment_reply(post_id: int, comment_id: int, text: str) -> dict:
    url = "https://api.vk.com/method/wall.createComment"
    params = {
        "owner_id": settings.vk_bot.GROUP_ID,
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": text,
        "access_token": settings.vk_bot.ACCESS_TOKEN,
        "v": "5.199"
    }

    # Синхронный запрос
    response = requests.post(url, params=params)
    data = response.json()  # Парсим JSON ответ
    return data


# Функция для ответа на личное сообщение
def send_private_message(user_id: int, text: str) -> dict:
    url = "https://api.vk.com/method/messages.send"
    params = {
        "peer_id": user_id, 
        "message": text,     
        "access_token": settings.vk_bot.ACCESS_TOKEN,
        "v": "5.199",    
        "random_id": 0    
    }

    # Синхронный запрос
    response = requests.post(url, params=params)
    data = response.json()  # Парсим JSON ответ
    return data


# Функция для получения текста поста
def get_post_text(post_id: int) -> str:
    access_token = settings.vk_bot.APP_TOKEN
    owner_id = settings.vk_bot.GROUP_ID
    posts = f'{owner_id}_{post_id}'

    url = f'https://api.vk.com/method/wall.getById?posts={posts}&access_token={access_token}&v=5.131'

    response = requests.get(url)
    data = response.json()

    if 'response' in data:
        post_text = data['response'][0]['text']
        return post_text
    else:
        print("Ошибка при получении данных:", data)
        return ""


# Извлекает сообщение бота и значение UF_CRM_1742556333 из текста
def parse_vk_bot_response(text: str):
    order_info_match = re.search(r'"UF_CRM_1742556333":\s*"(.+?)"', text)
    article_match = re.search(r'"UF_CRM_1742556276":\s*"(.+?)"', text)
    count_match = re.search(r'"UF_CRM_1742556311":\s*"(.+?)"', text)
    
    order_info = order_info_match.group(1) if order_info_match else None
    article = article_match.group(1) if article_match else None
    count = count_match.group(1) if count_match else None
    
    message = text.split("\n")[0]  # Первое предложение до пустой строки
    
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