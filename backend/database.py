from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import load_config


class Base(DeclarativeBase):
    pass


config = load_config()
engine = create_engine(config.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from . import models

    Base.metadata.create_all(bind=engine)
