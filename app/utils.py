from telebot.apihelper import ApiTelegramException

from .bot import bot
from .keyboards import create_kb_task, create_kb_task_edit, create_kb_tasklist

from database.db_funcs import get_current_tasks, get_task_by_id
from database.init_db import Task

# CONSTS
ALL_MESSAGE_TYPES = [
    'text', 'photo', 'video', 'audio', 'document', 'sticker','animation',
    'voice', 'video_note', 'contact', 'location','venue', 'poll', 'dice',
    'game', 'invoice','successful_payment', 'passport_data', 'chat_member',
    'chat_join_request'
]


# ToDo прикольное решение моей проблемы
# Функция для экранирования специальных символов в MarkdownV2
def escape_markdown_v2(text):
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def text_for_reply_to_bad_input(for_what: str) -> str:
    """
    [описания, названия] -> for_what, текст имеет следующий вид:

    Пожалуйста, отправьте текстовое сообщение для {for_what} задачи!
    (без специальных символов)"""
    return (f"Пожалуйста, "
            f"отправьте текстовое сообщение для {for_what} задачи! "
            f"(без специальных символов)")


def get_task_id(call_data) -> Task.id:
    """returns the Task.id by splitting call.data"""
    return int(call_data.split("_")[-1])


def delete_msg(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except ApiTelegramException:
        pass
        # logging.error(f"Ошибка: {e}")


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
        mark = "✅" if task.status == "completed" else "❌"
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Название: {task.title} {mark}\n\n"
                 f"Описание: {task.description}",
            reply_markup=create_kb_task(task)
        )
    else:
        update_tasklist(message)


def update_message_task(task_id, message):
    task = get_task_by_id(task_id)
    if task is not None:
        mark = "✅" if task.status == "completed" else "❌"
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Название: {task.title} {mark}\n\n"
                 f"Описание: {task.description}",
            reply_markup=create_kb_task(task)
        )
    else:
        update_tasklist(message)


def update_message_task_edit(task_id, message):
    task = get_task_by_id(task_id)
    if task is not None:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Название: {task.title}\n\n"
                 f"Описание: {task.description}",
            reply_markup=create_kb_task_edit(task.id)
        )
    else:
        update_tasklist(message)