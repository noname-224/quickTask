from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, engine
from domain.enums import TaskStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    is_premium: Mapped[bool | None]
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", uselist=True, lazy="joined")

    def __repr__(self):
        return (f"User(id={self.id}, username={self.username}, first_name={self.first_name}, "
                f"last_name={self.last_name}, is_premium={self.is_premium})")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.UNCOMPLETED)
    status_changed_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="tasks", uselist=False)

    def __repr__(self):
        return (f"Task(id={self.id}, title={self.title}, description={self.description}, user_id={self.user_id}), "
                f"status={self.status}, status_changed_at={self.status_changed_at})")


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)