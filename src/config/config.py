from os import getenv

from dotenv import load_dotenv


class Settings:
    load_dotenv()

    BOT_TOKEN = getenv("BOT_TOKEN")

    DB_HOST = getenv("DB_HOST")
    DB_PORT = getenv("DB_PORT")
    DB_USER = getenv("DB_USER")
    DB_PASS = getenv("DB_PASS")
    DB_NAME = getenv("DB_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
