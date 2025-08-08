from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from helpers.exceptions import UserNotFound
from helpers.type_hints import UserId, TaskId
from .database import engine, User, Task
from .sql_enums import TaskStatus


# ---------- User
def add_user(
        user_id: UserId, username: str, first_name: str,
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
        try:
            session.add(user)
            session.commit()
        except IntegrityError:
            pass



# ---------- Task
def add_task(title: str, description: str, user_id: UserId) -> None:
    with Session(engine) as session:
        if user := session.get(User, user_id):
            task = Task(title=title, description=description)
            user.tasks.append(task)  # ToDo Так и не понял что с этим делать (про подчеркивание)
            session.commit()
        else:
            raise UserNotFound


def get_tasks(user_id: UserId) -> list[Task]:
    with Session(engine) as session:
        if user := session.get(User, user_id):
            tasks = list(user.tasks)  # ToDo Так и не понял что с этим делать (про подчеркивание)
            return tasks
        else:
            raise UserNotFound


def get_task(task_id: TaskId) -> Task | None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        return task


def mark_task_completed(task_id: TaskId) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = TaskStatus.COMPLETED
        session.commit()


def mark_task_uncompleted(task_id: TaskId) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = TaskStatus.UNCOMPLETED
        session.commit()


def delete_task(task_id: TaskId) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        session.delete(task)
        session.commit()


def edit_task(task_id: TaskId,
              title: str | None = None,
              description: str | None = None) -> None:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.title, task.description = \
            title or task.title, description or task.description
        session.commit()