from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .sql_enums import TaskStatus
from helpers.config import Settings


class Base(DeclarativeBase):
    # __abstract__ = True
    #
    # id: Mapped[int] = mapped_column(
    #     Integer, primary_key=True, autoincrement=True)
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    is_premium: Mapped[bool | None]
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user",
        uselist=True,
        lazy="joined",
    )

    def __repr__(self):
        return (f"User(id={self.id}, username={self.username}, "
                f"first_name={self.first_name}, last_name={self.last_name}, "
                f"is_premium={self.is_premium})")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[TaskStatus] = mapped_column(
        default=TaskStatus.UNCOMPLETED)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tasks",
        uselist=False
    )

    def __repr__(self):
        return (f"Task(id={self.id}, title={self.title}, "
                f"description={self.description}, "
                f"status={self.status}, user_id={self.user_id})")


engine = create_engine(Settings.DB_PATH, echo=False)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
