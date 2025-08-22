from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.config import Settings


class Base(DeclarativeBase):
    pass

engine = create_engine(Settings.DB_PATH, echo=False)
session_factory = sessionmaker(engine)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)