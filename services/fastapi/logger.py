import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Callable

import aiokafka
from aiokafka.errors import KafkaConnectionError
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class KafkaLogger:
    """Асинхронный Kafka логгер с встроенной сериализацией."""
    def __init__(self, bootstrap_servers: str, service_name: str, topic: str = "app-logs"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.service_name = service_name
        self.producer: aiokafka.AIOKafkaProducer = None
        self._serializer = lambda v: json.dumps(v).encode("utf-8")  # Сериализатор здесь

    async def start(self, max_retries: int = 20, initial_delay: int = 5, backoff_factor: float = 1.5):
        """Запуск продюсера с правильным сериализатором"""
        self.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=self._serializer  # Используем наш сериализатор
        )
        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                await self.producer.start()
                print("Kafka producer успешно запущен.")
                return
            except KafkaConnectionError as e:
                if attempt == max_retries:
                    print(f"Ошибка: по истечении {max_retries} попыток подключения к Kafka, завершение.")
                    raise e
                print(f"Попытка {attempt}/{max_retries} не удалась: {e}. Повтор через {delay} секунд.")
                await asyncio.sleep(delay)
                delay *= backoff_factor

    async def stop(self):
        """Остановка Kafka продюсера."""
        if self.producer:
            await self.producer.stop()

    async def log(self, level: str, context: Dict[str, Any]):
        """Автоматическая сериализация в JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": self.service_name,
            "context": context,
        }
        
        # Добавьте отладочный вывод
        print("Sending log to Kafka:", json.dumps(log_entry, indent=2))
        
        try:
            if self.producer:
                await self.producer.send_and_wait(self.topic, log_entry)
            else:
                print("Продюсер не запущен. Лог-запись:", self._serializer(log_entry))
        except Exception as e:
            print(f"Ошибка отправки лога: {str(e)}")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware, которое логгирует каждый входящий запрос, ответ и возникающие ошибки.
    """
    def __init__(self, app, logger: KafkaLogger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Логирование входящего запроса
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
        }
        await self.logger.log("info", {"event": "incoming_request", "request": request_data})

        try:
            response = await call_next(request)
        except Exception as e:
            # Логирование ошибки, если происходит исключение
            await self.logger.log("error", {"event": "exception", "error": str(e)})
            raise e

        # Логирование отправленного ответа
        response_data = {
            "status_code": response.status_code,
        }
        await self.logger.log("info", {"event": "response_sent", "response": response_data})
        return response 