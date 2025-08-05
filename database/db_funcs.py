from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Sequence

from type_hints import User_id, Task_id
from .init_db import engine, User, Task


# ---------- User
def add_new_user(
        user_id: User_id, username: str, first_name: str,
        last_name: str | None = None,
        is_premium: bool | None = None) -> None:
    with Session(engine) as session:
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_premium=is_premium
        )

        session.merge(user)
        session.commit()


# ---------- Task
def add_new_task(title: str, description: str, user_id: User_id) -> None:
    with Session(engine) as session:

        task = Task(
            title=title,
            description=description,
            user_id=user_id
        )

        session.add(task)
        session.commit()


# Todo оставить так или выйти в None
def get_current_tasks(user_id: User_id) -> Sequence[Task]:
    with Session(engine) as session:
        stmt = select(Task).where(Task.user_id == user_id)
        tasks = session.scalars(stmt).fetchall()
        print(tasks)
        print(type(tasks))
        return tasks


def get_task_by_id(task_id: Task_id) -> Task | None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        return task


def mark_task_completed(task_id: Task_id) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = "completed"
        session.commit()


def mark_task_uncompleted(task_id: Task_id) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = "uncompleted"
        session.commit()


def delete_task(task_id: Task_id) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        session.delete(task)
        session.commit()


def edit_task(task_id: Task_id,
              title: str | None = None,
              description: str | None = None) -> None:
    with Session(engine) as session:
        if title and description:
            task = session.get(Task, task_id)
            task.title, task.description = title, description
        elif title:
            task = session.get(Task, task_id)
            task.title = title
        elif description:
            task = session.get(Task, task_id)
            task.description = description

        session.commit()