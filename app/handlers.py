from telebot.types import Message, CallbackQuery

from enum_classes import ForWhat
from .bot import bot
from .keyboards import create_kb_cancel_to_add
from .utils import (text_for_reply_to_bad_input, get_task_id,
                   show_tasklist, update_tasklist, show_message_task,
                   update_message_task, update_message_task_edit)
from database.db_funcs import (add_new_user, add_new_task, get_task_by_id,
                               mark_task_completed, mark_task_uncompleted,
                               delete_task, edit_task)
from type_hints import Id
from weather.weather import main


@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def show_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)


@bot.message_handler(commands=['view_tasks'])
def view_tasks_handler(message: Message) -> None:
    show_tasklist(message)


# @bot.callback_query_handler(func=lambda call: call.data == "remove_tasklist")
# def remove_tasklist(call):
#     delete_msg(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_by_btn(call: CallbackQuery) -> None:
    add(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_completed_"))
def bot_mark_task_completed(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    mark_task_completed(task_id)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_uncompleted_"))
def bot_mark_task_uncompleted(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    mark_task_uncompleted(task_id)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def bot_delete_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    delete_task(task_id)
    update_tasklist(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_msg"))
def bot_edit_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task_edit(task_id, call.message)


@bot.callback_query_handler(func=lambda call: call.data == "return")
def handle_return(call: CallbackQuery) -> None:
    update_tasklist(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("return_to_task_"))
def return_to_task(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_title_"))
def edit_title(call: CallbackQuery) -> None:
    # delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_title(msg, task_id, start_msg_id)
    )


def update_title(message: Message, task_id: Id, start_msg_id: Id) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input(ForWhat.TITLE),)
        bot.register_next_step_handler(
            message, lambda msg: update_title(msg, task_id, start_msg_id))
        return

    edit_task(task_id=task_id, title=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    show_message_task(task_id, message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_description"))
def edit_description(call: CallbackQuery) -> None:
    # delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_description(msg, task_id, start_msg_id)
    )

def update_description(
        message: Message, task_id: Id, start_msg_id: Id) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(ForWhat.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: update_description(msg, task_id, start_msg_id)
        )
        return

    edit_task(task_id=task_id, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    show_message_task(task_id, message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_all"))
def edit_all(call: CallbackQuery) -> None:
    # delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
    )

def edit_all_get_title(
        message: Message, task_id: Id, start_msg_id: Id) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input(ForWhat.TITLE))
        bot.register_next_step_handler(
            message,
            lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
        )
        return

    title = message.text

    task = get_task_by_id(task_id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        message,lambda msg: update_all(msg, task_id, start_msg_id, title))

def update_all(
        message: Message, task_id: Id, start_msg_id: Id, title: str) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(ForWhat.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message, lambda msg: update_all(msg, task_id, start_msg_id, title))
        return

    edit_task(task_id=task_id, title=title, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    show_message_task(task_id, message)


# - Команды [/start, /help] -
@bot.message_handler(commands=['start'])
def show_about(message: Message) -> None:
    add_new_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_premium=message.from_user.is_premium
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет {message.chat.first_name}!\n"
             "Я твой персональный ToDo-бот"
    )



def add(message: Message) -> None:
    # delete_msg(message.chat.id, message.id)


    start_msg_id = message.message_id + 1

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите название задачи",
        reply_markup = create_kb_cancel_to_add()

    )
    bot.register_next_step_handler(
        message, lambda msg: handle_add_title(msg, start_msg_id))

def handle_add_title(message: Message, start_msg_id: Id) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input(ForWhat.TITLE))
        bot.register_next_step_handler(
            message, lambda msg: handle_add_title(msg, start_msg_id))
        return

    title = message.text

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите описание задачи",
        reply_markup = create_kb_cancel_to_add()
    )
    bot.register_next_step_handler(
        message, lambda msg: handle_add_description(msg, title, start_msg_id))

def handle_add_description(
        message: Message, title: str, start_msg_id: Id) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(ForWhat.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message, lambda msg: handle_add_description(
                msg, title, start_msg_id))
        return

    description = message.text
    add_new_task(title, description, message.chat.id)

    bot.delete_messages(
        message.chat.id, list(range(start_msg_id, message.message_id + 1)))

    show_tasklist(message)


@bot.message_handler(content_types=['text'])
def weather(message: Message) -> None:
    bot.send_message(
        chat_id=message.chat.id,
        text=main(message.text)
    )