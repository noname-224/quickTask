from app.handlers import bot


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling()