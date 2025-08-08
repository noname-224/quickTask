from typing import Sequence

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.database import Task
from helpers.type_hints import TaskId


def create_kb_task(task: Task) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="return"))
    keyboard.row(
        InlineKeyboardButton(
            text="Редактировать", callback_data=f"edit_msg_{task.id}"),
        InlineKeyboardButton(
            text="Удалить", callback_data=f"delete_{task.id}")
    )
    if task.status == 'uncompleted':
        keyboard.add(InlineKeyboardButton(
            text="Выполнить",
            callback_data=f"mark_completed_{task.id}")
        )
    else:
        keyboard.add(InlineKeyboardButton(
            text="Добавить в незавершенные",
            callback_data=f"mark_uncompleted_{task.id}")
        )

    return keyboard


def create_kb_tasklist(tasks: Sequence[Task]) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup()
    for task in tasks:
        mark = "✅" if task.status == "completed" else "❌"
        keyboard.row(InlineKeyboardButton(
            text=f"{task.title} {mark}",
            callback_data=f"task_{task.id}",
        ))

    keyboard.row(
        InlineKeyboardButton(
            text="Закрыть", callback_data="remove_tasklist"),
        InlineKeyboardButton(
            text="Добавить", callback_data="add_task")
    )

    return keyboard


def create_kb_task_edit(task_id: TaskId) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Назад", callback_data=f"return_to_task_{task_id}"))
    keyboard.add(InlineKeyboardButton(
        text="Изменить название", callback_data=f"edit_title_{task_id}"))
    keyboard.add(InlineKeyboardButton(
        text="Изменить описание", callback_data=f"edit_description_{task_id}"))
    keyboard.add(InlineKeyboardButton(
        text="Изменить все", callback_data=f"edit_all_{task_id}"))
    return keyboard


def create_kb_cancel_to_add() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Отменить", callback_data="cancel_adding"))
    return keyboard


def create_kb_cancel_to_edit() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Отменить", callback_data="cancel_editing"))
    return keyboard

