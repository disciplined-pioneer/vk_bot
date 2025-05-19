import requests

VK_ACCESS_TOKEN="vk1.a.Ky0wxlpHEU97ml2RH8nUXGRw5zBSXMLmRHFCeTbJH4FM6_T4Mrl_k7YtPjq9rYvbAoP5jkMTydVFlWk2aPhgl5Q-aZ7DWMu4hCMIMb7OgAHBdis8Ls2sM0SenAfXKF3FmhcWpQnaSEcpKkvQnX6S4aOG3-PTdj6hBIR4HHTck93zWkRyErb5xGsMzZta9v3yRTdotFiRN9dw1fxgmKRCug"

USER_ID = 503427794  # id пользователя
COUNT = 20  # сколько сообщений получить

params = {
    'access_token': VK_ACCESS_TOKEN,
    'v': '5.154',
    'user_id': USER_ID,
    'count': COUNT
}

response = requests.get('https://api.vk.com/method/messages.getHistory', params=params)
data = response.json()

for msg in data['response']['items']:
    print(f"[{msg['from_id']}]: {msg['text']}")
