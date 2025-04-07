from quart import Quart
from pyngrok import ngrok
from settings import settings
from core.mongo import init_mongo
from bot.handlers.vk_handler import vk_callback

app = Quart(__name__)

# Подключаем Mongo
@app.before_serving
async def startup():
    await init_mongo()

# Добавляем маршрут для VK
app.add_url_rule("/", "vk_callback", vk_callback, methods=["POST"])

if __name__ == "__main__":
    ngrok.set_auth_token(settings.ngrok.TOKEN)
    public_url = ngrok.connect(5000).public_url
    print(f"🌐 Ngrok URL: {public_url}", flush=True)

    app.run(host="0.0.0.0", port=5000)
