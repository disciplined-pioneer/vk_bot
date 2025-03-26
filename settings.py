from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class MongoConfig(BaseSettings):
    PORT: int
    HOST: str

    class Config:
        env_prefix = 'Mongo_'
        env_file = '.env'
        extra = 'ignore'

    @property
    def URL(self) -> str:
        return f"mongodb://{self.HOST}:{self.PORT}"

class Settings:

    mongo = MongoConfig()

settings = Settings()
