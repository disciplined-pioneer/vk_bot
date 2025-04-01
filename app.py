from quart import Quart
from core.mongo import init_mongo
from bot.handlers.vk_handler import vk_callback


app = Quart(__name__)


# Инициализация MongoDB
async def init_db():
    await init_mongo()


@app.before_serving
async def before_serving():
    await init_db()


# Маршрут
app.add_url_rule("/", "vk_callback", vk_callback, methods=["POST"])


if __name__ == "__main__":

    # Запускаем сервер Quart
    app.run(host="0.0.0.0", port=5000)
