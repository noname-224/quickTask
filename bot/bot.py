from dotenv import load_dotenv
from os import getenv
from telebot import TeleBot


load_dotenv()
bot = TeleBot(getenv("BOT_TOKEN"))

# Предлагаю сделать отдельный файл settings, и создать там такой класс
#
# class Settings:
#     BOT_TOKEN = getenv("BOT_TOKEN")
#     DB_PATH = getenv("DB_PATH")
#     ....
#
# тогда ты сможешь импортировать этот класс в другие файлы без getenv, это выглядит более удобно + у тебя все настройки будут в 1 файле, а не разбросаны по всему проекту
#
#
#
#
