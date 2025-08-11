from dotenv import load_dotenv
from os import getenv


load_dotenv()

class Settings:
    BOT_TOKEN = getenv('BOT_TOKEN')
    DB_PATH = getenv('DB_PATH')
    OPENWEATHER_API_KEY = getenv('OPENWEATHER_API_KEY')

OPENWEATHER_URL_TEMPLATE = (
    "https://api.openweathermap.org/data/2.5/weather?"
    "lat={latitude}&lon={longitude}&"
    "appid=" + Settings.OPENWEATHER_API_KEY + "&lang=ru"
    "&units=metric"
)
