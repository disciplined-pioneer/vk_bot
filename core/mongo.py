from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from settings import settings

from db.beanie.models import document_models

client = AsyncIOMotorClient(settings.mongo.URL)


async def init_mongo():
    await init_beanie(
        database=client["mydatabase"],
        document_models=document_models
    )
