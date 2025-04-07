from quart import Quart, request

app = Quart(__name__)

@app.route("/", methods=["GET"])
async def index():
    print("👀 GET-запрос получен")
    return "✅ Сервер работает"
