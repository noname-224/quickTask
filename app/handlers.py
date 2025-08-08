from telebot.types import Message, CallbackQuery

from .bot import bot
from .services import edit_task_title, edit_task_description, edit_task_all, \
    add_task
from .utils import get_task_id, show_tasklist, update_tasklist, \
    update_message_task, update_message_task_edit
from database.db_funcs import add_new_user, mark_task_completed, \
    mark_task_uncompleted, delete_task
from weather.weather import main


@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def change_window_from_checklist_to_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)


@bot.message_handler(commands=['view_checklist'])
def show_checklist_window(message: Message) -> None:
    show_tasklist(message)


@bot.callback_query_handler(func=lambda call: call.data == "remove_tasklist")
def delete_checklist_window(call: CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_by_clicking(call: CallbackQuery) -> None:
    add_task(call.message)  # Todo изменить название


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_completed_"))
def bot_mark_task_completed(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    mark_task_completed(task_id)
    update_message_task(task_id, call.message)  # Todo изменить название


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_uncompleted_"))
def bot_mark_task_uncompleted(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    mark_task_uncompleted(task_id)
    update_message_task(task_id, call.message)  # Todo изменить название


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_task_from_checklist(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    delete_task(task_id)
    update_tasklist(call.message)  # Todo изменить название


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_msg"))
def change_window_from_task_to_task_edit(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task_edit(task_id, call.message)  # Todo изменить название


@bot.callback_query_handler(func=lambda call: call.data == "return")
def change_window_from_task_to_checklist(call: CallbackQuery) -> None:
    update_tasklist(call.message)  # Todo изменить название


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("return_to_task_"))
def change_window_from_task_edit_to_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)  # Todo изменить название


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_title_"))
def start_editing_task_title(call: CallbackQuery) -> None:
    edit_task_title(call)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_description"))
def start_editing_task_description(call: CallbackQuery) -> None:
    edit_task_description(call)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_all"))
def start_editing_task_all(call: CallbackQuery) -> None:
    edit_task_all(call)


# - Команды [/start, /help] -
@bot.message_handler(commands=['start'])
def show_start_message(message: Message) -> None:
    add_new_user(
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
             f"/view_checklist – просмотреть список задач"
    )


@bot.message_handler(content_types=['text'])
def weather(message: Message) -> None:
    bot.send_message(
        chat_id=message.chat.id,
        text=main(message.text)
    )