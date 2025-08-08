from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from typing import Optional

from helpers.exceptions import UserNotFound
from .bot import bot
from .keyboards import task_window_buttons, task_edit_window_buttons, checklist_window_buttons
from database.db_funcs import get_tasks, get_task
from .app_enums import TaskAttributeText, MessageUploadMethod
from helpers.type_hints import TaskId, MessageId, ChatId


# CONSTS
ALL_MESSAGE_TYPES = [
    'text', 'photo', 'video', 'audio', 'document', 'sticker','animation',
    'voice', 'video_note', 'contact', 'location','venue', 'poll', 'dice',
    'game', 'invoice','successful_payment', 'passport_data', 'chat_member',
    'chat_join_request'
]


# ToDo прикольное решение моей проблемы
# Функция для экранирования специальных символов в MarkdownV2
def escape_markdown_v2(text: str) -> str:
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def text_for_reply_to_bad_input(attribute: TaskAttributeText) -> str:
    return (f"Пожалуйста, "
            f"отправьте текстовое сообщение для {attribute} задачи! "
            f"(без специальных символов)")


def get_task_id(call_data: Optional[str]) -> TaskId:
    return int(call_data.split("_")[-1])


def safely_delete_message_from_chat(
        chat_id: ChatId, message_id: MessageId) -> None:
    try:
        bot.delete_message(chat_id, message_id)
    except ApiTelegramException:
        bot.send_message(
            chat_id=chat_id,
            text="Не удалось удалить сообщения из-за ошибки, "
                 "пожалуйста удалите вручную"
        )


def upload_checklist_window(
        message: Message, upload_method: MessageUploadMethod) -> None:
    try:
        if tasks := get_tasks(message.chat.id):
            text = "Вот твои задачи.\nНажми чтобы перейти к описанию"
        else:
            text = "У тебя нет задач!"

        if upload_method.value:
            bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=checklist_window_buttons(tasks)
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=text,
                reply_markup=checklist_window_buttons(tasks)
            )
    except UserNotFound:
        bot.send_message(
        chat_id=message.chat.id,
        text="Ты не авторизован.\n"
             "Отправь команду /start для авторизации"
        )


def upload_task_window(task_id: TaskId, message: Message,
                       upload_method: MessageUploadMethod) -> None:
    task = get_task(task_id)
    if task is not None:
        mark = "✅" if task.status == "completed" else "❌"
        if upload_method.value:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Название: {task.title} {mark}\n\n"
                     f"Описание: {task.description}",
                reply_markup=task_window_buttons(task)
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"Название: {task.title} {mark}\n\n"
                     f"Описание: {task.description}",
                reply_markup=task_window_buttons(task)
            )
    else:
        upload_checklist_window(message, MessageUploadMethod.UPDATE)


def upload_task_edit_window(task_id: TaskId, message: Message) -> None:
    task = get_task(task_id)
    if task is not None:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Название: {task.title}\n\n"
                 f"Описание: {task.description}",
            reply_markup=task_edit_window_buttons(task.id)
        )
    else:
        upload_checklist_window(message, MessageUploadMethod.UPDATE)
