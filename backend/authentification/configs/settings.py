from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    POSTGRESQL_USER: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DBNAME: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str
    TOKENS_SECRET_KEY: str
    ALGORYTHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_USERNAME: str
    KEYCLOAK_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
