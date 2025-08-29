from dotenv import load_dotenv
from os import getenv


class Settings:
    load_dotenv()


    BOT_TOKEN = getenv('BOT_TOKEN')


    DB_HOST = getenv('DB_HOST')
    DB_PORT = getenv('DB_PORT')
    DB_USER = getenv('DB_USER')
    DB_PASS = getenv('DB_PASS')
    DB_NAME = getenv('DB_NAME')
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    OPENWEATHER_API_KEY = getenv('OPENWEATHER_API_KEY')
    @property
    def OPENWEATHER_URL(self) -> str:
        return "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=" + \
            self.OPENWEATHER_API_KEY + "&lang=ru&units=metric"


settings = Settings()