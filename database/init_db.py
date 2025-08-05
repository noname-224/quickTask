from sqlalchemy import create_engine
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from config import Settings


class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="uncompleted")
    user_id: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return (f"Task(id={self.id}, title={self.title}, "
                f"description={self.description}, "
                f"status={self.status}, user_id={self.user_id})")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String, default=None)
    phone_number: Mapped[str] = mapped_column(String, default= )

    def __repr__(self):
        return (f"User(id={self.id}, username={self.username}, "
                f"first_name={self.first_name}, last_name={self.last_name}, "
                f"phone_number={self.phone_number})")


engine = create_engine(Settings.DB_PATH, echo=False)
Base.metadata.create_all(engine)
