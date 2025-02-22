from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Создаем движок для подключения к базе данных SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создаем локальную сессию для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 