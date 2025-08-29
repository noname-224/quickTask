from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.config import settings


class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, echo=False)
session_factory = sessionmaker(engine)