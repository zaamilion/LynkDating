from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_ENDPOINT_URL: str | None = None
    AWS_DEFAULT_REGION: str = "auto"
    AWS_GLOBAL_NAME: str
    AWS_S3_FILE_EXPIRE: int = 3600
    AUTHENTIFICATION_SERVICE_HOST: str
    AUTHENTIFICATION_SERVICE_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()
