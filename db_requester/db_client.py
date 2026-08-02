from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from resources.db_creds import DBCreds

engine = create_engine(
    f"postgresql+psycopg2://{DBCreds.USER}:{DBCreds.PASSWORD}@{DBCreds.HOST}:{DBCreds.PORT}/{DBCreds.NAME}",
    echo=False
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()