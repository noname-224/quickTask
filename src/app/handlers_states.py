from telebot.types import CallbackQuery, Message

from app.bot import bot
from app.states import BotStateMachine
from domain.types import message_types


# Обработка команды '/view_checklist'
@bot.message_handler(func=lambda message: True, content_types=message_types)
def _show_checklist_window(message: Message) -> None:
    bsm = BotStateMachine(message.from_user.id, message=message)
    bsm.handle()


@bot.callback_query_handler(func=lambda call: True)
def _start_adding_task_by_clicking(call: CallbackQuery) -> None:
    bsm = BotStateMachine(call.message.chat.id, call=call)
    bsm.handle()


# @bot.callback_query_handler(func=lambda call: call.data == "add_task_by_clicking")
# def _start_adding_task_by_clicking(call: CallbackQuery) -> None:
#     bsm = BotStateMachine(call.message.chat.id, call=call)
#     bsm.handle()
