import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    PLIVO_AUTH_ID = os.environ.get("PLIVO_AUTH_ID", "")
    PLIVO_AUTH_TOKEN = os.environ.get("PLIVO_AUTH_TOKEN", "")
    PLIVO_NUMBER = os.environ.get("PLIVO_NUMBER", "")
