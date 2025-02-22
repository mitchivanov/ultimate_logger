import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Generator, List
import asyncio
from aiokafka.errors import KafkaConnectionError
import logging
import json
from datetime import datetime

# Импортируем настройки БД, модели и схемы
from database import SessionLocal, engine
import models
import schemas
from logger import KafkaLogger, LoggingMiddleware

# Создаем таблицы, если они ещё не существуют (с проверкой существования)
try:
    models.Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    print(f"Ошибка при создании таблиц: {str(e)}")

app = FastAPI()

# 1. Создаем логгер и регистрируем middleware СРАЗУ ПОСЛЕ СОЗДАНИЯ APP
kafka_logger = KafkaLogger(
    bootstrap_servers="kafka:9092", 
    service_name="fastapi_service",
    topic="app-logs"
)
app.add_middleware(LoggingMiddleware, logger=kafka_logger)  # <--- ЕДИНСТВЕННЫЙ ВЫЗОВ

logger = logging.getLogger(__name__)




@app.on_event("startup")
async def startup_event():
    # Добавим задержку и повторные попытки подключения
    max_retries = 10
    retry_delay = 10  # секунд
    
    for attempt in range(max_retries):
        try:
            await kafka_logger.start()
            print(f"Successfully connected to Kafka on attempt {attempt + 1}")
            break
        except Exception as e:
            if attempt == max_retries - 1:  # Последняя попытка
                raise e
            print(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

@app.on_event("shutdown")
async def shutdown_event():
    # Логируем событие остановки приложения
    await kafka_logger.log("info", {"event": "shutdown", "message": "FastAPI сервис останавливается"})
    
    # Останавливаем Kafka продюсер
    await kafka_logger.stop()

# Зависимость для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для создания нового продукта с логированием операций с базой данных и ошибок
@app.post("/products", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Логируем начало операции создания продукта
    await kafka_logger.log("debug", {"event": "create_product_start", "product": product.dict()})
    
    # Проверяем, существует ли продукт с таким же именем
    db_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if db_product:
        # Логируем ошибку при попытке создать дублирующий продукт
        await kafka_logger.log("error", {
            "event": "create_product_error",
            "message": "Продукт с таким именем уже существует",
            "product": product.dict()
        })
        raise HTTPException(status_code=400, detail="Продукт с таким именем уже существует")
    
    new_product = models.Product(name=product.name, description=product.description)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Логируем успешное создание продукта
    await kafka_logger.log("info", {"event": "create_product_success", "product_id": new_product.id})
    return new_product

# Эндпоинт для получения списка продуктов с логированием начала и завершения операции
@app.get("/products", response_model=List[schemas.ProductResponse])
async def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Логируем начало операции получения списка продуктов
    await kafka_logger.log("debug", {"event": "read_products_start", "skip": skip, "limit": limit})
    products = db.query(models.Product).offset(skip).limit(limit).all()
    # Логируем успешное выполнение операции и количество полученных записей
    await kafka_logger.log("info", {"event": "read_products_success", "count": len(products)})
    return products

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
