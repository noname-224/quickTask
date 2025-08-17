from telebot.types import Message, CallbackQuery

from database.repositories import UserRepository, TaskRepository
from domain.enums import MessageUploadMethod, CancelledOperationName
from app.bot import bot
from .services import TaskModifier, WindowLoader
from utils.helpers import GetIdFromCallData
# from weather.weather import get_weather_text


# Обработка команды '/view_checklist'
@bot.message_handler(commands=['view_checklist'])
def _show_checklist_window(message: Message) -> None:
    WindowLoader.checklist(message, MessageUploadMethod.SEND)


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_window_to_task_edit_"))
def _change_window_to_task_edit(call: CallbackQuery) -> None:
    task_id = GetIdFromCallData.task_id(call.data)
    WindowLoader.task_edit(task_id, call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_window_to_task_"))
def _change_window_to_task(call: CallbackQuery) -> None:
    task_id = GetIdFromCallData.task_id(call.data)
    WindowLoader.task(task_id, call.message, MessageUploadMethod.UPDATE)


@bot.callback_query_handler(func=lambda call: call.data == "change_window_to_checklist")
def _change_window_to_checklist(call: CallbackQuery) -> None:
    WindowLoader.checklist(call.message, MessageUploadMethod.UPDATE)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_task_title_"))
def _start_editing_task_title(call: CallbackQuery) -> None:
    TaskModifier.edit_title(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_task_description_"))
def _start_editing_task_description(call: CallbackQuery) -> None:
    TaskModifier.edit_description(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_task_all_"))
def _start_editing_task_all(call: CallbackQuery) -> None:
    TaskModifier.edit_all(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_from_checklist_"))
def _delete_task_from_checklist(call: CallbackQuery) -> None:
    task_id = GetIdFromCallData.task_id(call.data)
    task_repo = TaskRepository()
    task_repo.delete(task_id)
    WindowLoader.checklist(call.message, MessageUploadMethod.UPDATE)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mark_task_completed_"))
def _bot_mark_task_completed(call: CallbackQuery) -> None:
    task_id = GetIdFromCallData.task_id(call.data)
    task_repo = TaskRepository()
    task_repo.mark_completed(task_id)
    WindowLoader.task(task_id, call.message, MessageUploadMethod.UPDATE)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mark_task_uncompleted_"))
def _bot_mark_task_uncompleted(call: CallbackQuery) -> None:
    task_id = GetIdFromCallData.task_id(call.data)
    task_repo = TaskRepository()
    task_repo.mark_uncompleted(task_id)
    WindowLoader.task(task_id, call.message, MessageUploadMethod.UPDATE)


@bot.callback_query_handler(func=lambda call: call.data == "delete_checklist_window")
def _delete_checklist_window(call: CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "add_task_by_clicking")
def _start_adding_task_by_clicking(call: CallbackQuery) -> None:
    TaskModifier.add(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_task_adding_"))
def _cancel_task_adding(call: CallbackQuery) -> None:
    TaskModifier.cancel_modify(call, CancelledOperationName.ADDITION)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_task_editing_"))
def _cancel_task_editing(call: CallbackQuery) -> None:
    TaskModifier.cancel_modify(call, CancelledOperationName.EDITING)


# Обработка команды '/start'
@bot.message_handler(commands=['start'])
def _show_message_start(message: Message) -> None:
    user_repo = UserRepository()
    user_repo.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_premium=message.from_user.is_premium
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет {message.chat.first_name}! "
             f"Я твой персональный ToDo-бот.\n\n"
             f"Ты можешь управлять мной, посылая эти команды:\n\n"
             f"/view_checklist – просмотреть список задач\n"
             f"или отправь название города, "
             f"а я расскажу про погоду в этом регионе"
    )




# --------------------------------------------------------------------- Обработка запросов про погоду
# @bot.message_handler(content_types=['text'])
# def _show_message_weather(message: Message) -> None:
#     bot.send_message(
#         chat_id=message.chat.id,
#         text=get_weather_text(message.text)
#     )