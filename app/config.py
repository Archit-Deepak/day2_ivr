import os
from dotenv import load_dotenv

load_dotenv()


# Vercel/Neon hand out a "postgres://" URL, but SQLAlchemy 1.4+ requires the
# "postgresql://" scheme. Normalize whichever name the integration injected.
_db = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or ""
if _db.startswith("postgres://"):
    _db = _db.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = _db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get("REDIS_URL") or os.environ.get("KV_URL") or "redis://localhost:6379"
    PLIVO_AUTH_ID = os.environ.get("PLIVO_AUTH_ID", "")
    PLIVO_AUTH_TOKEN = os.environ.get("PLIVO_AUTH_TOKEN", "")
    PLIVO_NUMBER = os.environ.get("PLIVO_NUMBER", "")
