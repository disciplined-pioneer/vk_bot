import requests
from settings import settings


access_token = settings.vk_bot.APP_TOKEN

#access_token = '310cc60f310cc60f310cc60f7832212ebc3310c310cc60f56e94421333b91e99013d519'
print(access_token)

owner_id = settings.vk_bot.GROUP_ID

post_id = '259'

# Формируем строку для параметра "posts"
posts = f'{owner_id}_{post_id}'

url = f'https://api.vk.com/method/wall.getById?posts={posts}&access_token={access_token}&v=5.131'

response = requests.get(url)
data = response.json()

print(data)