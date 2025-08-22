from typing import Sequence

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.base import Task
from domain.enums import TaskStatus
from domain.types import TaskId, MessageId


class InlineKeyboardCreator:
    @staticmethod
    def create_task_window_buttons(task: Task) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                text="↩️️ Назад",
                callback_data="change_window_to_checklist")
        )
        keyboard.row(
            InlineKeyboardButton(
                text="✏️ Редактировать",
                callback_data=f"change_window_to_task_edit_{task.id}"
            ),
            InlineKeyboardButton(
                text="🗑️ Удалить",
                callback_data=f"delete_task_from_checklist_{task.id}")
        )
        if task.status == TaskStatus.COMPLETED:
            keyboard.add(InlineKeyboardButton(
                text="❌ Отменить выполнение",
                callback_data=f"mark_task_uncompleted_{task.id}")
            )

        else:
            keyboard.add(InlineKeyboardButton(
                text="✅ Выполнить",
                callback_data=f"mark_task_completed_{task.id}")
            )
        return keyboard

    @staticmethod
    def create_checklist_window_buttons(tasks: Sequence[Task]) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardMarkup()
        for task in tasks:
            mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"
            keyboard.row(InlineKeyboardButton(
                text=f"{task.title} {mark}",
                callback_data=f"change_window_to_task_{task.id}",
            ))

        keyboard.row(
            InlineKeyboardButton(
                text="✖️ Закрыть", callback_data="delete_checklist_window"),
            InlineKeyboardButton(
                text="➕ Добавить", callback_data="add_task_by_clicking")
        )
        return keyboard

    @staticmethod
    def create_task_edit_window_buttons(task_id: TaskId) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text="↩️️ Назад",
            callback_data=f"change_window_to_task_{task_id}"))
        keyboard.add(InlineKeyboardButton(
            text="Изменить название",
            callback_data=f"edit_task_title_{task_id}"))
        keyboard.add(InlineKeyboardButton(
            text="Изменить описание",
            callback_data=f"edit_task_description_{task_id}"))
        keyboard.add(InlineKeyboardButton(
            text="Изменить все",
            callback_data=f"edit_task_all_{task_id}"))
        return keyboard

    @staticmethod
    def create_cancel_adding_button(start_msg_id: MessageId) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="↩️ Отменить", callback_data=f"cancel_task_adding_{start_msg_id}"))
        return keyboard

    @staticmethod
    def create_cancel_editing_button(start_msg_id: MessageId) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="↩️ Отменить", callback_data=f"cancel_task_editing_{start_msg_id}"))
        return keyboard