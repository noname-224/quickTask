# ----- Imports -----
import logging

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

from time import sleep

from database import (init_db, add_new_task, get_current_tasks, delete_task,
                      mark_task_completed, mark_task_uncompleted, edit_task,
                      get_task_by_id)


# ----- Logging setup -----
logging.basicConfig(level=logging.ERROR, filename='bot.log')

# ----- Initializations -----
TOKEN = "8069638628:AAEQhoDjYwXWi_MdkjjjgLHw0gXuF1DIumU"
bot = TeleBot(TOKEN)
init_db()


# ----- BOT -----



# --- Функции для укорочения кода ---

def get_task_id(call):
    return int(call.data.split("_")[-1])

def delete_msg(chat_id, message_id):
    """Удаляет одно любое сообщение.
    Не приводящее к ошибке, в случае неудачи."""
    try:
        bot.delete_message(chat_id, message_id)
    except ApiTelegramException as e:
        logging.error(f"Ошибка: {e}")


def show_tasklist(message):
    tasks = get_current_tasks(message.chat.id)
    if tasks:
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию"
    else:
        text = "У тебя нет задач!"

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=create_kb_tasklist(tasks)
    )


def update_tasklist(message):
    tasks = get_current_tasks(message.chat.id)
    if tasks:
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию"
    else:
        text = "У тебя нет задач!"

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=create_kb_tasklist(tasks)
    )


def show_message_task(task_id, message):
    task = get_task_by_id(task_id)

    if task is not None:
        if task[3] == "completed":
            msg_text = f"Название: {task[1]} ✅\n\nОписание:\n{task[2]}"
        else:
            msg_text = f"Название: {task[1]} ❌\n\nОписание:\n{task[2]}"

        bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=create_kb_task(task[0])
        )
    else:
        update_tasklist(message)


def update_message_task(task_id, message):
    task = get_task_by_id(task_id)

    if task is not None:
        if task[3] == "completed":
            msg_text = f"Название: {task[1]} ✅\n\nОписание:\n{task[2]}"
        else:
            msg_text = f"Название: {task[1]} ❌\n\nОписание:\n{task[2]}"

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=msg_text,
            reply_markup=create_kb_task(task[0])
        )
    else:
        update_tasklist(message)


def update_message_task_edit(task_id, message):
    task = get_task_by_id(task_id)

    if task is not None:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Название: {task[1]}\nОписание: {task[2]}",
            reply_markup=create_kb_task_edit(task[0])
        )
    else:
        update_tasklist(message)


# --- Обработчики команд ---

# - Команда /view_tasks -
# Создание клавиатур
def create_kb_task(task_id):
    task = get_task_by_id(task_id)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Назад", callback_data="return"))
    kb.row(
        InlineKeyboardButton(
            "Редактировать", callback_data=f"edit_msg_{task_id}"),
        InlineKeyboardButton(
            "Удалить", callback_data=f"delete_{task_id}")
    )
    if task[3] == 'uncompleted':
        kb.add(InlineKeyboardButton(
            "Выполнить",
            callback_data=f"mark_completed_{task_id}")
        )
    else:
        kb.add(InlineKeyboardButton(
            "Добавить в незавершенные",
            callback_data=f"mark_uncompleted_{task_id}")
        )

    return kb

def create_kb_tasklist(tasks):

    kb = InlineKeyboardMarkup()
    for task in tasks:
        if task[3] == "completed":
            btn_text = f"{task[1]} ✅"
        else:
            btn_text = f"{task[1]} ❌"

        kb.row(InlineKeyboardButton(
            btn_text,
            callback_data=f"task_{task[0]}",
            parse_mode="HTML"
        ))

    kb.row(
        InlineKeyboardButton(
            "Закрыть", callback_data="remove_tasklist"),
        InlineKeyboardButton(
            "Добавить", callback_data="add_task")
    )

    return kb

def create_kb_task_edit(task_id):
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton(
        "Назад", callback_data=f"return_to_task_{task_id}"))
    kb.add(InlineKeyboardButton(
        "Изменить название", callback_data=f"edit_title_{task_id}"))
    kb.add(InlineKeyboardButton(
        "Изменить описание", callback_data=f"edit_description_{task_id}"))
    kb.add(InlineKeyboardButton(
        "Изменить все", callback_data=f"edit_all_{task_id}"))

    return kb



# Обработка команды /view_tasks
@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def show_task(call):
    # user_id = call.message.chat.id
    # task_index = get_task_id(call)
    # task = get_task_by_index(user_id, task_index)

    task_id = call.data.split("_")[-1]

    update_message_task(task_id, call.message)

@bot.message_handler(commands=['view_tasks'])
def view_tasks_handler(message):
    delete_msg(message.chat.id, message.message_id)

    show_tasklist(message)

@bot.callback_query_handler(func=lambda call: call.data == "remove_tasklist")
def remove_tasklist(call):
    bot.delete_message(
        chat_id=call.message.chat.id,message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_by_btn(call):
    add(call.message)

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_completed_"))
def bot_mark_task_completed(call):
    task_id = get_task_id(call)
    mark_task_completed(task_id)
    update_message_task(task_id, call.message)

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_uncompleted_"))
def bot_mark_task_uncompleted(call):
    task_id = get_task_id(call)
    mark_task_uncompleted(task_id)
    update_message_task(task_id, call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def bot_delete_task(call):
    task_id = get_task_id(call)
    delete_task(task_id)
    update_tasklist(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_msg"))
def bot_edit_task(call):
    task_id = get_task_id(call)
    update_message_task_edit(task_id, call.message)

@bot.callback_query_handler(func=lambda call: call.data == "return")
def handle_return(call):
    update_tasklist(call.message)

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("return_to_task_"))
def return_to_task(call):
    update_message_task(get_task_id(call), call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_title_"))
def edit_title(call):
    delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        call.message.chat.id,
        f"Текущее название задачи: ```{task[1]}``` Напишите новое название задачи",
        parse_mode="Markdown",)

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_title(msg, task_id, start_msg_id)
    )


def update_title(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для названия задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message, lambda msg: update_title(msg, task_id, start_msg_id))
        return

    edit_task(task_id, title=message.text)

    bot.send_message(
        message.chat.id, "Изменения сохранены")

    for msg_id in range(start_msg_id, message.message_id + 1):
        try:
            bot.delete_message(message.chat.id, msg_id)
            sleep(0.05)
        except ApiTelegramException as e:
            logging.error(f"Ошибка: {e}")

    show_message_task(task_id, message)

    sleep(5)
    delete_msg(message.chat.id, message.message_id + 1)



@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_description"))
def edit_description(call):
    delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        call.message.chat.id, "Напишите новое описание задачи")

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_description(msg, task_id, start_msg_id)
    )

def update_description(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для описания задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message,
            lambda msg: update_description(msg, task_id, start_msg_id)
        )
        return

    edit_task(task_id, description=message.text)

    bot.send_message(
        message.chat.id, "Изменения сохранены")

    for msg_id in range(start_msg_id, message.message_id + 1):
        try:
            bot.delete_message(message.chat.id, msg_id)
            sleep(0.05)
        except ApiTelegramException as e:
            logging.error(f"Ошибка: {e}")

    show_message_task(task_id, message)

    sleep(5)
    delete_msg(message.chat.id, message.message_id + 1)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_all"))
def edit_all(call):
    delete_msg(call.message.chat.id, call.message.id)

    task_id = get_task_id(call)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        call.message.chat.id, "Напишите новое название задачи")

    bot.register_next_step_handler(
        call.message,
        lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
    )

def edit_all_get_title(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для названия задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message,
            lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
        )
        return

    title = message.text

    bot.send_message(message.chat.id, "Напишите новое описание задачи")

    bot.register_next_step_handler(
        message,lambda msg: update_all(msg, task_id, start_msg_id, title))

def update_all(message, task_id, start_msg_id, title):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для описания задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message, lambda msg: update_all(msg, task_id, start_msg_id, title))
        return

    edit_task(task_id, title=title, description=message.text)

    bot.send_message(message.chat.id, "Изменения сохранены")

    for msg_id in range(start_msg_id, message.message_id + 1):
        try:
            bot.delete_message(message.chat.id, msg_id)
            sleep(0.05)
        except ApiTelegramException as e:
            logging.error(f"Ошибка: {e}")

    show_message_task(task_id, message)

    sleep(5)
    delete_msg(message.chat.id, message.message_id + 1)



# - Команды [/start, /help] -
@bot.message_handler(commands=['start', 'help'])
def show_about(message):
    bot.send_message(
        message.chat.id,
        f"Привет {message.chat.first_name}!\n"
        f"Я твой персональный ToDo-бот"
    )


# - Команда /add_task -
@bot.message_handler(commands=['add_task'])
def add(message):
    delete_msg(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Напишите название задачи")
    bot.register_next_step_handler(
        message, lambda msg: handle_add_title(msg, message.message_id))

def handle_add_title(message, command_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для названия задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message, lambda msg: handle_add_title(msg, command_id))
        return

    title = message.text

    bot.send_message(message.chat.id, "Напишите описание задачи")
    bot.register_next_step_handler(
        message, lambda msg: handle_add_description(msg, title, command_id))

def handle_add_description(message, title, command_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message,
            "Пожалуйста, "
            "отправьте текстовое сообщение для описания задачи! "
            "(без специальных символов)")
        bot.register_next_step_handler(
            message, lambda msg: handle_add_description(
                msg, title, command_id))
        return

    description = message.text
    add_new_task(title, description, message.chat.id)

    bot.send_message(
        message.chat.id,
        f"<u><b>Задача сохранена!</b></u>\n"
        f"Название — {title}\nОписание: {description}",
        parse_mode="HTML"
    )

    for msg_id in range(command_id + 1, message.message_id + 1):
        try:
            bot.delete_message(message.chat.id, msg_id)
            sleep(0.05)
        except ApiTelegramException as e:
            logging.error(f"Ошибка: {e}")

    show_tasklist(message)

    sleep(5)
    delete_msg(message.chat.id, message.message_id + 1)


# - перехват сообщений всех типов -
@bot.message_handler(
    content_types=['text', 'photo', 'video', 'audio', 'document', 'sticker',
                   'animation', 'voice', 'video_note', 'contact', 'location',
                   'venue', 'poll', 'dice', 'game', 'invoice',
                   'successful_payment', 'passport_data', 'chat_member',
                   'chat_join_request'])
def handle(message):
    delete_msg(message.chat.id, message.message_id)
    # show_about(message)
    # sleep(5)
    # delete_msg(message.chat.id, message.message_id + 1)

# ----- Main -----
if __name__ == "__main__":
    bot.skip_pending = True
    bot.polling()