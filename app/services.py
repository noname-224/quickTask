# Отработка запросов ввода у пользователя

from telebot.types import CallbackQuery, Message

from app.app_enums import TaskAttributeText, MessageUploadMethod
from app.bot import bot
from app.keyboards import cancel_adding_button
from app.utils import get_task_id, text_for_reply_to_bad_input, \
    upload_task_window, upload_checklist_window
from database.db_funcs import get_task, edit_task, add_task
from helpers.exceptions import UserNotFound
from helpers.type_hints import TaskId, MessageId


# -----------------------------------------------------------------------------
def add_new_task(message: Message) -> None:
    # safely_delete_message_from_chat(message.chat.id, message.id)

    start_msg_id = message.message_id + 1

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите название задачи",
        reply_markup = cancel_adding_button()
    )
    bot.register_next_step_handler(
        message, lambda msg: __add_new_task_second_step(msg, start_msg_id))


def __add_new_task_second_step(message: Message, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
        )
        bot.register_next_step_handler(
            message, lambda msg: __add_new_task_second_step(msg, start_msg_id))
        return

    title = message.text

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите описание задачи",
        reply_markup = cancel_adding_button()
    )
    bot.register_next_step_handler(
        message, lambda msg: __add_new_task_final_step(msg, title, start_msg_id))


def __add_new_task_final_step(
        message: Message, title: str, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message, lambda msg: __add_new_task_final_step(
                msg, title, start_msg_id))
        return

    description = message.text
    try:
        add_task(title, description, message.chat.id)
    except UserNotFound:
        bot.send_message(
            chat_id=message.chat.id,
            text="Вы не авторизованы.\n"
                 "Отправьте команду /start для авторизации"
        )
    bot.delete_messages(
        message.chat.id, list(range(start_msg_id, message.message_id + 1)))

    upload_checklist_window(message, MessageUploadMethod.SEND)


# -----------------------------------------------------------------------------
def edit_task_title(call: CallbackQuery) -> None:
    # safely_delete_message_from_chat(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task(task_id)
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
        lambda msg: __edit_task_title_final_step(msg, task_id, start_msg_id)
    )


def __edit_task_title_final_step(
        message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
        )
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_title_final_step(msg, task_id, start_msg_id))
        return

    edit_task(task_id=task_id, title=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    upload_task_window(task_id, message, MessageUploadMethod.SEND)


# -----------------------------------------------------------------------------
def edit_task_description(call: CallbackQuery) -> None:
    # safely_delete_message_from_chat(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task(task_id)
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
        lambda msg: __edit_task_description_final_step(msg, task_id, start_msg_id)
    )


def __edit_task_description_final_step(
        message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: __edit_task_description_final_step(msg, task_id, start_msg_id)
        )
        return

    edit_task(task_id=task_id, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    upload_task_window(task_id, message, MessageUploadMethod.SEND)


# -----------------------------------------------------------------------------
def edit_task_all(call: CallbackQuery) -> None:
    # safely_delete_message_from_chat(call.message.chat.id, call.message.id)

    task_id = get_task_id(call.data)
    task = get_task(task_id)
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
        lambda msg: __edit_task_all_next_step(msg, task_id, start_msg_id)
    )


def __edit_task_all_next_step(
        message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: __edit_task_all_next_step(msg, task_id, start_msg_id)
        )
        return

    title = message.text

    task = get_task(task_id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        message,lambda msg: __edit_task_all_final_step(msg, task_id, start_msg_id, title))


def __edit_task_all_final_step(
        message: Message,
        task_id: TaskId, start_msg_id: MessageId, title: str) -> None:
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,
            text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
        )
        bot.register_next_step_handler(
            message, lambda msg: __edit_task_all_final_step(msg, task_id, start_msg_id, title))
        return

    edit_task(task_id=task_id, title=title, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    upload_task_window(task_id, message, MessageUploadMethod.SEND)