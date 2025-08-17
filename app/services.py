# Отработка запросов ввода у пользователя
from telebot.types import CallbackQuery, Message

from database.base import Task
from database.repositories import TaskRepository
from domain.enums import TaskAttributeText, MessageUploadMethod, CancelledOperationName, TaskStatus
from app.bot import bot
from app.keyboards import InlineKeyboardCreator
from domain.exceptions import UserNotFound
from utils.helpers import GetIdFromCallData, text_for_reply_to_bad_input
from domain.types import TaskId, MessageId


class WindowLoader:

    @staticmethod
    def checklist(message: Message, upload_method: MessageUploadMethod) -> None:
        try:
            task_repo = TaskRepository()
            tasks = task_repo.get_all(user_id=message.chat.id)

            if tasks:
                text = "Вот твои задачи.\nНажми чтобы перейти к описанию"
            else:
                text = "У тебя нет задач!"

            if upload_method.value:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=text,
                    reply_markup=InlineKeyboardCreator.checklist_window_buttons(tasks)
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=text,
                    reply_markup=InlineKeyboardCreator.checklist_window_buttons(tasks)
                )
        except UserNotFound:
            bot.send_message(
                chat_id=message.chat.id,
                text="Ты не авторизован.\n"
                     "Отправь команду /start для авторизации"
            )

    @staticmethod
    def task(task_id: TaskId, message: Message,
                           upload_method: MessageUploadMethod) -> None:
        task_repo = TaskRepository()
        task = task_repo.get_one(task_id)
        if task is not None:
            mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"
            if upload_method.value:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"Название: {task.title} {mark}\n\n"
                         f"Описание: {task.description}",
                    reply_markup=InlineKeyboardCreator.task_window_buttons(task)
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=f"Название: {task.title} {mark}\n\n"
                         f"Описание: {task.description}",
                    reply_markup=InlineKeyboardCreator.task_window_buttons(task)
                )
        else:
            # TODO это правильное использование (я про WindowLoader.)?
            WindowLoader.checklist(message, MessageUploadMethod.UPDATE)

    @staticmethod
    def task_edit(task_id: TaskId, message: Message) -> None:
        task_repo = TaskRepository()
        task = task_repo.get_one(task_id=task_id)
        if task is not None:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"Название: {task.title}\n\n"
                     f"Описание: {task.description}",
                reply_markup=InlineKeyboardCreator.task_edit_window_buttons(task.id)
            )
        else:
            # TODO это правильное использование (я про WindowLoader.)?
            WindowLoader.checklist(message, MessageUploadMethod.UPDATE)


class TaskModifier:

    @staticmethod
    def add(message: Message) -> None:
        start_msg_id = message.message_id
        bot.send_message(
            chat_id=message.chat.id,
            text="Напишите название задачи",
            reply_markup=InlineKeyboardCreator.cancel_adding_button(start_msg_id + 1)
        )
        bot.register_next_step_handler(
            # TODO это правильное использование (я про TaskModifier.)?
            message, lambda msg: TaskModifier.__add_second_step(msg, start_msg_id))

    @staticmethod
    def __add_second_step(message: Message, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__add_second_step(msg, start_msg_id))
            return

        title = message.text

        bot.send_message(
            chat_id=message.chat.id,
            text="Напишите описание задачи",
            reply_markup=InlineKeyboardCreator.cancel_adding_button(start_msg_id + 1)
        )
        bot.register_next_step_handler(
            message, lambda msg: TaskModifier.__add_final_step(msg, title, start_msg_id))

    @staticmethod
    def __add_final_step(message: Message, title: str, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__add_final_step(msg, title, start_msg_id))
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

        # bot.delete_messages(message.chat.id, list(range(start_msg_id, message.message_id + 1)))
        WindowLoader.checklist(message, MessageUploadMethod.SEND)

    # -----------------------------------------------------------------------------
    @staticmethod
    def edit_title(call: CallbackQuery) -> None:
        task_id = GetIdFromCallData.task_id(call.data)
        task_repo = TaskRepository()
        task = task_repo.get_one(task_id)
        start_msg_id = call.message.message_id

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>название</b></u>: "
                 f"<code>{task.title}</code>\n\n"
                 f"Напишите новое <u><b>название</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.cancel_editing_button(start_msg_id + 1)
        )
        bot.register_next_step_handler(
            call.message, lambda msg: TaskModifier.__edit_title_final_step(msg, task_id, start_msg_id))

    @staticmethod
    def __edit_title_final_step(message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__edit_title_final_step(msg, task_id, start_msg_id))
            return

        task_repo = TaskRepository()
        task_repo.edit(task_id=task_id, title=message.text)

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
        WindowLoader.task(task_id, message, MessageUploadMethod.SEND)

    # -----------------------------------------------------------------------------
    @staticmethod
    def edit_description(call: CallbackQuery) -> None:
        task_id = GetIdFromCallData.task_id(call.data)
        task_repo = TaskRepository()
        task = task_repo.get_one(task_id)
        start_msg_id = call.message.message_id

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>описание</b></u>: "
                 f"<code>{task.description}</code>\n\n"
                 f"Напишите новое <u><b>описание</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.cancel_editing_button(start_msg_id + 1)
        )

        bot.register_next_step_handler(
            call.message, lambda msg: TaskModifier.__edit_description_final_step(msg, task_id, start_msg_id))

    @staticmethod
    def __edit_description_final_step(message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__edit_description_final_step(msg, task_id, start_msg_id))
            return

        task_repo = TaskRepository()
        task_repo.edit(task_id=task_id, description=message.text)

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
        WindowLoader.task(task_id, message, MessageUploadMethod.SEND)

    # -----------------------------------------------------------------------------
    @staticmethod
    def edit_all(call: CallbackQuery) -> None:
        task_id = GetIdFromCallData.task_id(call.data)
        task_repo = TaskRepository()
        task = task_repo.get_one(task_id)
        start_msg_id = call.message.message_id

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>название</b></u>: "
                 f"<code>{task.title}</code>\n\n"
                 f"Напишите новое <u><b>название</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.cancel_editing_button(start_msg_id + 1)
        )

        bot.register_next_step_handler(
            call.message,
            lambda msg: TaskModifier.__edit_all_second_step(msg, task, start_msg_id)
        )

    @staticmethod
    def __edit_all_second_step(message: Message, task: Task, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.TITLE))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__edit_all_second_step(msg, task, start_msg_id))
            return

        title = message.text

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Текущее <u><b>описание</b></u>: "
                 f"<code>{task.description}</code>\n\n"
                 f"Напишите новое <u><b>описание</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.cancel_editing_button(start_msg_id + 1)
        )

        bot.register_next_step_handler(
            message, lambda msg: TaskModifier.__edit_all_final_step(msg, task, start_msg_id, title))

    @staticmethod
    def __edit_all_final_step(message: Message, task: Task, start_msg_id: MessageId, title: str) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(message=message, text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION))
            bot.register_next_step_handler(
                message, lambda msg: TaskModifier.__edit_all_final_step(msg, task, start_msg_id, title))
            return

        description = message.text

        task_repo = TaskRepository()
        task_repo.edit(task_id=task.id, title=title, description=description)

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.message_id + 1)))
        WindowLoader.task(task.id, message, MessageUploadMethod.SEND)
        
    @staticmethod
    def cancel_modify(call: CallbackQuery, cancelled_operation_name: CancelledOperationName) -> None:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        start_msg_id = GetIdFromCallData.message_id(call.data)
        bot.delete_messages(call.message.chat.id, list(range(start_msg_id, start_msg_id + 20)))
        bot.answer_callback_query(callback_query_id=call.id, text=f"{cancelled_operation_name} отменено")