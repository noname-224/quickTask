from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from database.base import session_factory
from database.models import User, Task
from domain.enums import TaskStatus
from domain.types import UserId, TaskId


class UserRepository:

    @staticmethod
    def add_user(user_id: UserId, username: str, first_name: str,
                 last_name: str | None = None,
                 is_premium: bool | None = None) -> None:
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_premium=is_premium
        )

        try:
            with session_factory() as session:
                session.add(user)
                session.commit()
        except IntegrityError:
            ...

    @staticmethod
    def get_user_by_id(user_id: UserId) -> User | None:
        with session_factory() as session:
            return session.get(User, user_id)


class TaskRepository:

    @staticmethod
    def add(title: str, description: str, user_id: UserId) -> None:
        task = Task(title=title, description=description, status_changed_at=datetime.now(), user_id=user_id)
        with session_factory() as session:
            session.add(task)
            session.commit()

    @staticmethod
    def get_one(task_id: TaskId) -> Task | None:
        with session_factory() as session:
            return session.get(Task, task_id)

    @staticmethod
    def get_all(user_id: UserId) -> list[Task] | None:
        stmt = (
            select(
                Task.id,
                Task.title,
                Task.description,
                Task.status_changed_at,
                Task.status
            )
            .where(Task.user_id == user_id)
            .order_by(Task.status.desc(), Task.status_changed_at.desc())
        )
        with session_factory() as session:
            tasks = session.execute(stmt).all()
            return tasks

    @staticmethod
    def mark_completed(task_id: TaskId) -> None:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskStatus.COMPLETED, status_changed_at=datetime.now())
        )
        with session_factory() as session:
            session.execute(stmt)
            session.commit()

    @staticmethod
    def mark_uncompleted(task_id: TaskId) -> None:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskStatus.UNCOMPLETED, status_changed_at=datetime.now())
        )
        with session_factory() as session:
            session.execute(stmt)
            session.commit()

    @staticmethod
    def delete(task_id: TaskId) -> None:
        stmt = (
            delete(Task)
            .where(Task.id == task_id)
        )
        with session_factory() as session:
            session.execute(stmt)
            session.commit()

    @staticmethod
    def edit(task_id: TaskId, title: str = None, description: str = None) -> None:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(
                title=title or Task.title,
                description=description or Task.description
            )
        )
        with session_factory() as session:
            session.execute(stmt)
            session.commit()