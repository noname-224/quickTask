from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, engine
from domain.enums import BotState, TaskStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    is_premium: Mapped[bool | None]
    state: Mapped[BotState] = mapped_column(default=BotState.STATE_MANAGER)
    context: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict,
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user"
    )

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

    user: Mapped["User"] = relationship(back_populates="tasks")

    def __repr__(self):
        return (f"Task(id={self.id}, title={self.title}, description={self.description}, user_id={self.user_id}), "
                f"status={self.status}, status_changed_at={self.status_changed_at})")


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)