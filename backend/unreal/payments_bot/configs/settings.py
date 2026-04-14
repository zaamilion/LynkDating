from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    POSTGRESQL_USER: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DBNAME: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str
    TELEGRAM_API_KEY: str
    PREMIUM_COST: int

    class Config:
        env_file = ".env"


settings = Settings()
