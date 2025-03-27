
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings
import asyncio

from db.beanie.models.models import Test

async def init():
    client = AsyncIOMotorClient(settings.mongo.URL)
    await init_beanie(database=client["reglament"], document_models=[
        Test
    ])

    
    client.close()