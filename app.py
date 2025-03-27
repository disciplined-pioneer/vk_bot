from quart import Quart
from pyngrok import ngrok
from core.mongo import init_mongo
from bot.handlers.vk_handler import vk_callback

app = Quart(__name__)

# Инициализация MongoDB
async def init_db():
    await init_mongo()

@app.before_serving
async def before_serving():
    await init_db()

# Пример маршрута Quart
app.add_url_rule("/", "vk_callback", vk_callback, methods=["POST"])

if __name__ == "__main__":
    # Запускаем ngrok и выводим URL
    public_url = ngrok.connect(5000).public_url
    print(f"Ngrok URL: {public_url}")

    # Запускаем сервер Quart
    app.run(host="0.0.0.0", port=5000)
