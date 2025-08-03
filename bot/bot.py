from dotenv import load_dotenv
from os import getenv
from telebot import TeleBot


load_dotenv()
bot = TeleBot(getenv("BOT_TOKEN"))