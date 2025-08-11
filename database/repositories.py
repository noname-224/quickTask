from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.base import engine, Task, User
from domain.enums import TaskStatus
from domain.exceptions import UserNotFound
from domain.types import UserId, TaskId


class SqlalchemyBaseRepository:
    ...


class UserRepository(SqlalchemyBaseRepository):

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
            with Session(engine) as session:
                session.add(user)
                session.commit()
        except IntegrityError:
            ...

    @staticmethod
    def get_user_by_id(user_id: UserId) -> User | None:
        with Session(engine) as session:
            return session.get(User, user_id)


class TaskRepository(SqlalchemyBaseRepository):

    @staticmethod
    def add(title: str, description: str, user_id: UserId) -> None:
        with Session(engine) as session:
            if user := session.get(User, user_id):
                task = Task(title=title, description=description)
                user.tasks.append(task)
                session.commit()
            else:
                raise UserNotFound('User does not exist')

    @staticmethod
    def get_one(task_id: TaskId) -> Task | None:
        with Session(engine) as session:
            return session.get(Task, task_id)

    @staticmethod
    def get_all(user_id: UserId) -> list[Task] | None:
        if user := UserRepository.get_user_by_id(user_id):
            tasks = list(user.tasks)
            return tasks
        else:
            raise UserNotFound('User does not exist')

    @staticmethod
    def mark_completed(task_id: TaskId) -> None:
        with Session(engine) as session:
            task = session.get(Task, task_id)
            task.status = TaskStatus.COMPLETED
            session.commit()

    @staticmethod
    def mark_uncompleted(task_id: TaskId) -> None:
        with Session(engine) as session:
            task = session.get(Task, task_id)
            task.status = TaskStatus.UNCOMPLETED
            session.commit()

    @staticmethod
    def delete(task_id: TaskId) -> None:
        with Session(engine) as session:
            task = session.get(Task, task_id)
            session.delete(task)
            session.commit()

    @staticmethod
    def edit(task_id: TaskId, title: str = None, description: str = None) -> None:
        with Session(engine) as session:
            task = session.get(Task, task_id)
            task.title, task.description = title or task.title, description or task.description
            session.commit()