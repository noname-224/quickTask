from telebot.types import Message, CallbackQuery

from app.bot import bot
from app.keyboards import InlineKeyboardCreator
from database.models import Task
from database.repositories import TaskRepository
from domain.enums import MessageUploadMethod, TaskStatus, TaskAttributeText, CancelledOperationName
from domain.types import TaskId, MessageId
from utils.helpers import text_for_reply_to_bad_input, get_task_id, get_message_id


class WindowLoaderService:
    task_repo = TaskRepository()

    @classmethod
    def load_checklist(cls, message: Message, upload_method: MessageUploadMethod) -> None:
        tasks = cls.task_repo.get_all(user_id=message.chat.id)
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию" if tasks else "У тебя нет задач!"

        if upload_method.value:
            bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=InlineKeyboardCreator.create_checklist_window_buttons(tasks)
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=text,
                reply_markup=InlineKeyboardCreator.create_checklist_window_buttons(tasks)
            )

    @classmethod
    def load_task(cls, task_id: TaskId, message: Message, upload_method: MessageUploadMethod) -> None:
        task = cls.task_repo.get_one(task_id)

        if task is not None:
            mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"

            if upload_method.value:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"Название: {task.title} {mark}\n\n"
                         f"Описание: {task.description}",
                    reply_markup=InlineKeyboardCreator.create_task_window_buttons(task)
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=f"Название: {task.title} {mark}\n\n"
                         f"Описание: {task.description}",
                    reply_markup=InlineKeyboardCreator.create_task_window_buttons(task)
                )
        else:
            cls.load_checklist(message, MessageUploadMethod.UPDATE)

    @classmethod
    def load_task_edit(cls, task_id: TaskId, message: Message) -> None:
        task = cls.task_repo.get_one(task_id=task_id)

        if task is not None:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"Название: {task.title}\n\n"
                     f"Описание: {task.description}",
                reply_markup=InlineKeyboardCreator.create_task_edit_window_buttons(task.id)
            )
        else:
            cls.load_checklist(message, MessageUploadMethod.UPDATE)


class TaskModifierService:
    task_repo = TaskRepository()

    @classmethod
    def add(cls, message: Message) -> None:
        start_msg_id = message.message_id + 1
        bot.send_message(
            chat_id=message.chat.id,
            text="Напишите название задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(start_msg_id)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: cls.__add_second_step(msg, start_msg_id)
        )

    @classmethod
    def __add_second_step(cls, message: Message, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__add_second_step(msg, start_msg_id)
            )
            return

        title = message.text

        bot.send_message(
            chat_id=message.chat.id,
            text="Напишите описание задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(start_msg_id)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: cls.__add_final_step(msg, title, start_msg_id)
        )

    @classmethod
    def __add_final_step(cls, message: Message, title: str, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__add_final_step(msg, title, start_msg_id)
            )
            return

        description = message.text

        cls.task_repo.add(
            title=title,
            description=description,
            user_id=message.chat.id
        )

        # bot.delete_messages(message.chat.id, list(range(start_msg_id, message.get_message_id + 1)))
        WindowLoaderService.load_checklist(message, MessageUploadMethod.SEND)


    # -----------------------------------------------------------------------------
    @classmethod
    def edit_title(cls, call: CallbackQuery) -> None:
        task_id = get_task_id(call.data)
        task = cls.task_repo.get_one(task_id)
        start_msg_id = call.message.message_id + 1

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>название</b></u>: <code>{task.title}</code>\n\n"
                 f"Напишите новое <u><b>название</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.create_cancel_editing_button(start_msg_id)
        )
        bot.register_next_step_handler(
            call.message,
            lambda msg: cls.__edit_title_final_step(msg, task_id, start_msg_id)
        )

    @classmethod
    def __edit_title_final_step(cls, message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__edit_title_final_step(msg, task_id, start_msg_id)
            )
            return

        title = message.text
        cls.task_repo.edit(
            task_id=task_id,
            title=title
        )

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.get_message_id + 1)))
        WindowLoaderService.load_task(task_id, message, MessageUploadMethod.SEND)


    # -----------------------------------------------------------------------------
    @classmethod
    def edit_description(cls, call: CallbackQuery) -> None:
        task_id = get_task_id(call.data)
        task = cls.task_repo.get_one(task_id)
        start_msg_id = call.message.message_id + 1

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>описание</b></u>: <code>{task.description}</code>\n\n"
                 f"Напишите новое <u><b>описание</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.create_cancel_editing_button(start_msg_id)
        )
        bot.register_next_step_handler(
            call.message,
            lambda msg: cls.__edit_description_final_step(msg, task_id, start_msg_id)
        )

    @classmethod
    def __edit_description_final_step(cls, message: Message, task_id: TaskId, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__edit_description_final_step(msg, task_id, start_msg_id)
            )
            return

        description = message.text
        cls.task_repo.edit(
            task_id=task_id,
            description=description
        )

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.get_message_id + 1)))
        WindowLoaderService.load_task(task_id, message, MessageUploadMethod.SEND)


    # -----------------------------------------------------------------------------
    @classmethod
    def edit_all(cls, call: CallbackQuery) -> None:
        task_id = get_task_id(call.data)
        task = cls.task_repo.get_one(task_id)
        start_msg_id = call.message.message_id + 1

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Текущее <u><b>название</b></u>: <code>{task.title}</code>\n\n"
                 f"Напишите новое <u><b>название</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.create_cancel_editing_button(start_msg_id)
        )
        bot.register_next_step_handler(
            call.message,
            lambda msg: cls.__edit_all_second_step(msg, task, start_msg_id)
        )

    @classmethod
    def __edit_all_second_step(cls, message: Message, task: Task, start_msg_id: MessageId) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__edit_all_second_step(msg, task, start_msg_id)
            )
            return

        title = message.text

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Текущее <u><b>описание</b></u>: "
                 f"<code>{task.description}</code>\n\n"
                 f"Напишите новое <u><b>описание</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.create_cancel_editing_button(start_msg_id)
        )
        bot.register_next_step_handler(
            message,
            lambda msg: cls.__edit_all_final_step(msg, task, start_msg_id, title)
        )

    @classmethod
    def __edit_all_final_step(cls, message: Message, task: Task, start_msg_id: MessageId, title: str) -> None:
        if message.content_type != 'text' or message.text.startswith('/'):
            bot.reply_to(
                message=message,
                text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
            )
            bot.register_next_step_handler(
                message,
                lambda msg: cls.__edit_all_final_step(msg, task, start_msg_id, title)
            )
            return

        description = message.text
        cls.task_repo.edit(
            task_id=task.id,
            title=title,
            description=description
        )

        # bot.delete_messages(message.chat.id,list(range(start_msg_id, message.get_message_id + 1)))
        WindowLoaderService.load_task(task.id, message, MessageUploadMethod.SEND)


    # -----------------------------------------------------------------------------
    @staticmethod
    def cancel_modify(call: CallbackQuery, cancelled_operation_name: CancelledOperationName) -> None:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        start_msg_id = get_message_id(call.data)
        bot.delete_messages(call.message.chat.id, list(range(start_msg_id, start_msg_id + 20)))
        bot.answer_callback_query(callback_query_id=call.id, text=f"{cancelled_operation_name} отменено")