from sqlalchemy import create_engine, Boolean, ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import Optional, List

from config import Settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean)
    # tasks: Mapped[List["Task"]] = relationship(
    #     back_populates="user", uselist=True)

    def __repr__(self):
        return (f"User(id={self.id}, username={self.username}, "
                f"first_name={self.first_name}, last_name={self.last_name}, "
                f"is_premium={self.is_premium})")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="uncompleted")
    user_id: Mapped[int] = mapped_column(Integer)
    # user: Mapped["User"] = relationship(back_populates="tasks", uselist=False)
    # user_fk: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def __repr__(self):
        return (f"Task(id={self.id}, title={self.title}, "
                f"description={self.description}, "
                f"status={self.status}, user_id={self.user_id})")


engine = create_engine(Settings.DB_PATH, echo=False)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
