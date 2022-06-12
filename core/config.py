from decouple import config
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = config("DB_URL")
    BDBaseModel = declarative_base()

    JWT_SECRET: str = config("JWR_SECRET")
    ALGORITHM: str = config("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    class Config:
        case_sensitive = True


settings = Settings()

'''
import secrets
token = secrets.token_urlsafe(32)
'''
