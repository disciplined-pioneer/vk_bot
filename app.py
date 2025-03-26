from flask import Flask, request
import requests
from pyngrok import ngrok

# Конфигурация
SECRET_KEY = "obama"
ACCESS_TOKEN = "vk1.a.Ky0wxlpHEU97ml2RH8nUXGRw5zBSXMLmRHFCeTbJH4FM6_T4Mrl_k7YtPjq9rYvbAoP5jkMTydVFlWk2aPhgl5Q-aZ7DWMu4hCMIMb7OgAHBdis8Ls2sM0SenAfXKF3FmhcWpQnaSEcpKkvQnX6S4aOG3-PTdj6hBIR4HHTck93zWkRyErb5xGsMzZta9v3yRTdotFiRN9dw1fxgmKRCug"
CONFIRMATION_TOKEN = "986e553a"
GROUP_ID = -229856852 

app = Flask(__name__)

# Множество для отслеживания ID комментариев
processed_comments = set()

@app.route("/", methods=["POST"])
def vk_callback():
    data = request.json
    print(f"\nReceived data: {data}")

    # Проверяем секретный ключ
    if "secret" in data and data["secret"] != SECRET_KEY:
        return "Invalid secret", 403

    # Подтверждение сервера ВК
    if data["type"] == "confirmation":
        return CONFIRMATION_TOKEN

    # Обрабатываем новый комментарий
    if data["type"] == "wall_reply_new":
        comment_text = data["object"]["text"]
        user_id = data["object"]["from_id"]
        post_id = data["object"]["post_id"]
        comment_id = data["object"]["id"]
        print(f"\ncomment_id = {comment_id}\n")

        print(f"\nНовый комментарий: {comment_text} от {user_id}")  # Логируем комментарий
        print(processed_comments)

        # Проверка: если комментарий от бота, не отвечать на него
        if user_id == GROUP_ID:
            print(f"Это комментарий от бота (ID: {user_id}), пропускаем.")
            return "ok"

        # Если на этот комментарий уже был отправлен ответ, пропускаем его
        if comment_id in processed_comments:
            print(f"Ответ уже отправлен на комментарий {comment_id}")
            return "ok"

        # Отправляем ответ на комментарий
        reply_text = f"Спасибо за комментарий! Мы свяжемся с вами."
        send_comment_reply(post_id, comment_id, reply_text)

        # Добавляем комментарий в множество обработанных
        processed_comments.add(comment_id)

    return "ok"

def send_comment_reply(post_id, comment_id, text):
    """Функция для ответа на комментарий"""
    url = "https://api.vk.com/method/wall.createComment"
    params = {
        "owner_id": GROUP_ID, 
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": text,
        "access_token": ACCESS_TOKEN,
        "v": "5.199"
    }
    response = requests.post(url, params=params)
    print(f"Response from VK API: {response.json()}") 
    return response.json()

if __name__ == "__main__":
    # Запускаем ngrok и выводим URL
    public_url = ngrok.connect(5000).public_url
    print(f"Ngrok URL: {public_url}")

    # Запускаем сервер Flask
    app.run(host="0.0.0.0", port=5000)
