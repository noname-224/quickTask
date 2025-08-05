from sqlalchemy.orm import Session

from type_hints import User_id, Task_id
from .database import engine, User, Task
from .sql_enums import TaskStatus


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
        task = Task(title=title, description=description)
        user = session.query(User).filter_by(id=user_id).first()
        user.tasks.append(task)  # ToDo Так и не понял что с этим делать (про подчеркивание)
        session.commit()


def get_current_tasks(user_id: User_id) -> list[Task]:
    with Session(engine) as session:
        user = session.get(User, user_id)
        tasks = list(user.tasks)  # ToDo Так и не понял что с этим делать (про подчеркивание)
        return tasks


def get_task_by_id(task_id: Task_id) -> Task | None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        return task


def mark_task_completed(task_id: Task_id) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = TaskStatus.COMPLETED  # ToDo Это правильно? (я про Enum)
        session.commit()


def mark_task_uncompleted(task_id: Task_id) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = TaskStatus.UNCOMPLETED   # ToDo Это правильно? (я про Enum)
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