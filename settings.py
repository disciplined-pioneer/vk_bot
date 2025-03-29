from pydantic_settings import BaseSettings


class VkBot(BaseSettings):
    SECRET: str
    ACCESS_TOKEN: str
    CONFIRMATION: str
    GROUP_ID: int
    APP_TOKEN: str

    class Config:
        env_prefix = 'VK_'
        env_file = '.env'
        extra = 'ignore'


class MongoConfig(BaseSettings):
    PORT: int
    HOST: str

    class Config:
        env_prefix = 'MONGO_'
        env_file = '.env'
        extra = 'ignore'

    @property
    def URL(self) -> str:
        return f"mongodb://{self.HOST}:{self.PORT}"


class GptConfig(BaseSettings):
    API_KEY: str
    BASE_URL: str

    class Config:
        env_prefix = 'GPT_'
        env_file = '.env'
        extra = 'ignore'

class Settings:

    vk_bot = VkBot()
    mongo = MongoConfig()
    gpt = GptConfig()

settings = Settings()
