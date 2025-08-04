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


engine = create_engine(Settings.DB_PATH, echo=False)
Base.metadata.create_all(engine)
