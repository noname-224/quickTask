# Отработка запросов ввода у пользователя
from telebot.types import CallbackQuery, Message

from database.base import Task
from database.repositories import TaskRepository
from domain.enums import TaskAttributeText, MessageUploadMethod
from app.bot import bot
from app.keyboards import InlineKeyboardCreator
from domain.exceptions import UserNotFound
from utils.helpers import get_task_id, text_for_reply_to_bad_input, \
    upload_task_window, upload_checklist_window
from domain.types import TaskId, MessageId


# -----------------------------------------------------------------------------
def add_new_task(message: Message) -> None:
    start_msg_id = message.message_id
    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите название задачи",
        reply_markup=InlineKeyboardCreator.cancel_adding_button()
    )
    bot.register_next_step_handler(
        message, lambda msg: __add_new_task_second_step(msg, start_msg_id))


def __add_new_task_second_step(message: Message, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
        bot.register_next_step_handler(
            message, lambda msg: __add_new_task_second_step(msg, start_msg_id))
        return

    title = message.text

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите описание задачи",
        reply_markup=InlineKeyboardCreator.cancel_adding_button()
    )
    bot.register_next_step_handler(
        message, lambda msg: __add_new_task_final_step(msg, title, start_msg_id))


def __add_new_task_final_step(message: Message, title: str, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
        bot.register_next_step_handler(
            message, lambda msg: __add_new_task_final_step(msg, title, start_msg_id))
        return

    description = message.text

    try:
        task_repo = TaskRepository()
        task_repo.add(
            title=title,
            description=description,
            user_id=message.chat.id
        )
    except UserNotFound:
        pass

    bot.delete_messages(message.chat.id, list(range(start_msg_id, message.message_id + 1)))
    upload_checklist_window(message, MessageUploadMethod.SEND)


# -----------------------------------------------------------------------------
def edit_task_title(call: CallbackQuery) -> None:
    task_id = get_task_id(call.data)
    task_repo = TaskRepository()
    task = task_repo.get_one(task_id)
    start_msg_id = call.message.message_id

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(
        call.message, lambda msg: __edit_task_title_final_step(msg, task_id, start_msg_id))


def __edit_task_title_final_step(message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_title_final_step(msg, task_id, start_msg_id))
        return

    task_repo = TaskRepository()
    task_repo.edit(task_id=task_id, title=message.text)

    bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
    upload_task_window(task_id, message, MessageUploadMethod.SEND)


# -----------------------------------------------------------------------------
def edit_task_description(call: CallbackQuery) -> None:
    # safely_delete_message_from_chat(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task_repo = TaskRepository()
    task = task_repo.get_one(task_id)
    start_msg_id = call.message.message_id

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message, lambda msg: __edit_task_description_final_step(msg, task_id, start_msg_id))


def __edit_task_description_final_step(message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_description_final_step(msg, task_id, start_msg_id))
        return

    task_repo = TaskRepository()
    task_repo.edit(task_id=task_id, description=message.text)

    bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
    upload_task_window(task_id, message, MessageUploadMethod.SEND)

# -----------------------------------------------------------------------------

def edit_task_all(call: CallbackQuery) -> None:
    # safely_delete_message_from_chat(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task_repo = TaskRepository()
    task = task_repo.get_one(task_id)
    start_msg_id = call.message.message_id

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: __edit_task_all_second_step(msg, task, start_msg_id)
    )


def __edit_task_all_second_step(message: Message, task: Task, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message,text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_all_second_step(msg, task, start_msg_id))
        return

    title = message.text

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        message,lambda msg: __edit_task_all_final_step(msg, task, start_msg_id, title))


def __edit_task_all_final_step(message: Message, task: Task, start_msg_id: MessageId, title: str) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_all_final_step(msg, task, start_msg_id, title))
        return

    description = message.text

    task_repo = TaskRepository()
    task_repo.edit(task_id=task.id, title=title, description=description)

    bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
    upload_task_window(task.id, message, MessageUploadMethod.SEND)