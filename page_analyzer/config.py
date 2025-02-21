import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения."""

    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    DATABASE_URL = os.getenv("DATABASE_URL")
