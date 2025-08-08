from typing import Sequence

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.database import Task
from database.sql_enums import TaskStatus
from helpers.type_hints import TaskId


def task_window_buttons(task: Task) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data="change_window_to_checklist")
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Редактировать",
            callback_data=f"change_window_to_task_edit_{task.id}"
        ),
        InlineKeyboardButton(
            text="Удалить",
            callback_data=f"delete_task_from_checklist_{task.id}")
    )
    if task.status == TaskStatus.UNCOMPLETED:
        keyboard.add(InlineKeyboardButton(
            text="Выполнить",
            callback_data=f"mark_task_completed_{task.id}")
        )
    else:
        keyboard.add(InlineKeyboardButton(
            text="Отменить выполнение",
            callback_data=f"mark_task_uncompleted_{task.id}")
        )
    return keyboard


def checklist_window_buttons(tasks: Sequence[Task]) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup()
    for task in tasks:
        mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"
        keyboard.row(InlineKeyboardButton(
            text=f"{task.title} {mark}",
            callback_data=f"change_window_to_task_{task.id}",
        ))

    keyboard.row(
        InlineKeyboardButton(
            text="Закрыть", callback_data="delete_checklist_window"),
        InlineKeyboardButton(
            text="Добавить", callback_data="add_task_by_clicking")
    )

    return keyboard


def task_edit_window_buttons(task_id: TaskId) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Назад", 
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


def cancel_adding_button() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Отменить", callback_data="cancel_task_adding"))
    return keyboard


def cancel_editing_button() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Отменить", callback_data="cancel_task_editing"))
    return keyboard

