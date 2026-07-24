from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Особенность SQLite для работы с несколькими потоками
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Зависимость (Dependency) для получения сессии БД в эндпоинтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        