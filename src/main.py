from app.handlers_states import bot


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling()