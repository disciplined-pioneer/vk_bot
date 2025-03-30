import requests
from settings import settings

# Функция для ответа на комментарий
def send_comment_reply(post_id, comment_id, text):
    
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
    print(f"\nAPI: {data}")
    return data


# Функция для получение текста поста
def get_post_text(post_id):

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

