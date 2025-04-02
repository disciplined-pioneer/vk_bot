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
    USER: str
    PASSWORD: str
    HOST: str
    PORT: str
    AUTH_DB: str

    class Config:
        env_prefix = 'MONGO_'
        env_file = '.env'
        extra = 'ignore'

    @property
    def URL(self) -> str:
        return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.AUTH_DB}"


class NgrokConfig(BaseSettings):
    TOKEN: str

    class Config:
        env_prefix = 'NGROK_'
        env_file = '.env'
        extra = 'ignore'


class GptConfig(BaseSettings):
    API_KEY: str
    BASE_URL: str

    class Config:
        env_prefix = 'GPT_'
        env_file = '.env'
        extra = 'ignore'


class BitrixConfig(BaseSettings):
    URL: str

    class Config:
        env_prefix = 'BITRIX_'
        env_file = '.env'
        extra = 'ignore'


class Settings:

    vk_bot = VkBot()
    mongo = MongoConfig()
    gpt = GptConfig()
    bitrix24 = BitrixConfig()
    ngrok = NgrokConfig()

settings = Settings()
