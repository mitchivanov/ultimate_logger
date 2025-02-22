from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=True)